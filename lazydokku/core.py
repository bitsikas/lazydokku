import json
import shlex
import datetime
import subprocess


class DokkuCommandExecutor:
    def __init__(self, dokku_bin: tuple):
        self.dokku_bin = tuple(dokku_bin)
        self._history = []

    @property
    def history(self):
        return "\n".join(
            f"> {h['stamp']}: {h['cmd']}\n{h['response'].decode()}\n" % h
            for h in self._history
        )

    def run(self, cmd, *args):

        stamp = datetime.datetime.now()
        try:
            output = subprocess.check_output(
                self.dokku_bin + (cmd,) + args, stderr=subprocess.DEVNULL
            )
            self._history.append(
                {
                    "cmd": shlex.join(self.dokku_bin + (cmd,) + args),
                    "response": output,
                    "stamp": stamp,
                }
            )
        except:
            self._history.append(
                {
                    "cmd": shlex.join(self.dokku_bin + (cmd,) + args),
                    "response": "error",
                    "stamp": stamp,
                }
            )
            return ""
        return output.decode()


class DokkuProvider:
    def __init__(self, executor):
        self.executor = executor
        self._apps = None
        self._config = dict()
        self._domains = dict()
        self._letsencrypt = dict()

    @property
    def apps(self):
        """Example output"""
        if self._apps is None:
            self._apps = [
                a.strip()
                for a in self.executor.run("apps:list").splitlines()[1:]
            ]
        return self._apps

    def add_app(self, new_app):
        self.executor.run("apps:create", new_app)
        if self._apps is None:
            self._apps = [new_app]
        else:
            self._apps.append(new_app)

    def config(self, app: str):
        """Example output
        =====> appname env vars
        KEY:        VALUE

        """
        if app not in self._config:
            self._config[app] = {}
            config = self.executor.run("config:show", app)
            for line in config.splitlines()[1:]:
                if ":" not in line.strip():
                    continue
                key, value = line.split(":", 1)
                value = value.strip()
                self._config[app][key] = value

        return self._config[app]

    def domains(self, app: str):
        """Example output"""
        if app not in self._domains:
            domains_output = self.executor.run("domains:report", app)
            info, enabled, vhosts, *_ = domains_output.splitlines()
            self._domains[app] = [
                d.strip() for d in vhosts.split(":", 1)[1].split()
            ]

        return self._domains[app]

    def add_domain(self, app, domain):
        self.executor.run("domains:add", app, domain)
        self._domains[app].append(domain)

    def letsencrypt(self, app):
        """Example output
        -----> App name           Certificate Expiry        Time before expiry        Time before renewal
        app_name                  2022-03-22 23:00:22       48d, 58m, 45s             18d, 58m, 45s
        """
        return "LE placeholder"
