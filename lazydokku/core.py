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
            f"> {i}: {h['stamp']}: {h['cmd']}\n{h['response']}\n"
            for i, h in enumerate(self._history)
        )

    def run(self, cmd, *args):

        stamp = datetime.datetime.now()
        try:
            output = subprocess.check_output(
                self.dokku_bin + (cmd,) + args, stderr=subprocess.DEVNULL
            ).decode()
        except:
            output = ""
        self._history.append(
            {
                "cmd": shlex.join(self.dokku_bin + (cmd,) + args),
                "response": output or "error",
                "stamp": stamp,
            }
        )
        return output


class DokkuConfig(dict):
    def __init__(
        self,
        app: str,
        executor: DokkuCommandExecutor,
        metadata: str,
        *args,
        **kwargs,
    ):
        self.executor = executor
        self.app = app
        super().__init__(*args, **kwargs)
        super().update(json.loads(metadata))

    def __setitem__(self, key, value):
        self.executor.run("config:set", self.app, key, value)
        self[key] = value

    def __delitem__(self, key):
        self.executor.run("config:unset", self.app, key)
        del self[key]


class DokkuDomains(list):
    def __init__(
        self,
        app: str = None,
        executor: DokkuCommandExecutor = None,
        metadata: list = None,
        *args,
        **kwargs,
    ):
        assert app is not None
        assert executor is not None
        assert metadata is not None
        self.app = app
        self.executor = executor
        info, enabled, vhosts, *_ = metadata
        assert (
            self.app in info
        ), f"Mismatching domains provided for {self.app}: {info}"
        super().__init__(*args, **kwargs)
        super().extend(vhosts.split(":", 1)[1].split())

    def append(self, item):
        self.executor.run("domains:add", self.app, item)
        super().append(item)


class DokkuApplication(dict):
    def __init__(
        self,
        name: str,
        metadata: str,
        domains: DokkuDomains,
        configs: DokkuConfig,
        executor: DokkuCommandExecutor,
    ):
        self.executor = executor
        self.name = name
        self.update(json.loads(metadata))
        #self.metadata = json.loads(metadata)
        self.domains = domains
        self.config = configs
        DokkuConfig(
            app=self.name,
            executor=self.executor,
            metadata=self.executor.run(
                "config:export", "--format=json", self.name
            ),
        )


class DokkuProvider(dict):
    def __init__(self, executor):
        self.executor = executor
        # self.refresh()

    def refresh(self, callback=None):

        app_list = [
            a.strip() for a in self.executor.run("apps:list").splitlines()[1:]
        ]
        app_metadata = self.executor.run(
            "apps:report", "--format", "json"
        ).splitlines()
        domains_list = []

        domains_output = self.executor.run("domains:report").splitlines()
        for start in range(len(domains_output))[0:None:5]:
            domains_list.append(domains_output[start : start + 5])
        for app, metadata, domains in zip(
            app_list, app_metadata, domains_list
        ):
            self[app] = DokkuApplication(
                name=app,
                executor=self.executor,
                domains=DokkuDomains(
                    app=app, executor=self.executor, metadata=domains
                ),
                configs=DokkuConfig(
                    app=app,
                    executor=self.executor,
                    metadata=self.executor.run(
                        "config:export", "--format=json", app
                    ),
                ),
                metadata=metadata,
            )
        if callback is not None:
            callback()

    @property
    def apps(self):
        return self.keys()

    def add_app(self, new_app):
        self.executor.run("apps:create", new_app)
        self.refresh()

    def __delitem__(self, key):

        self.executor.run("apps:destroy", "--force", key)
        super().__delitem__(key)

    def letsencrypt(self, app):
        """Example output
        -----> App name           Certificate Expiry        Time before expiry        Time before renewal
        app_name                  2022-03-22 23:00:22       48d, 58m, 45s             18d, 58m, 45s
        """
        return "LE placeholder"
