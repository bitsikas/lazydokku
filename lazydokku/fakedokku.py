
import faker
import random

dokku = faker.Faker()

class FakeDokkuCommandExecutor:
    history: list

    def __init__(self, dokku_bin: list):
        self.dokku_bin = dokku_bin
        self.history = []

    def apps_list(self):
        apps_output = "=====> My Apps\n"
        apps_output += "\n".join(dokku.domain_word() for _ in range(20))
        return apps_output

    def config_list(self, app):
        configs_output = f"=====> {app} env vars\n"
        for i in range(random.randint(0, 10)):

            configs_output += f"{app.upper()}_{dokku.domain_word().upper()}:  {dokku.domain_word().upper()}\n"
        return configs_output

    def domains_report(self, app):
        domains = " ".join(
            (f"{app}.%s" % dokku.domain_name())
            for _ in range(random.randint(1, 10))
        )
        return (
            f"=====> {app} domains information\n"
            "Domains app enabled:           true\n"
            f"Domains app vhosts:            {domains}\n"
            "Domains global enabled:        false\n"
            "Domains global vhosts:\n"
        )

    def run(self, cmd, *args):
        sargs = " ".join(args or [])
        self.history.append(f"{self.dokku_bin} {cmd} {sargs}")

        if cmd == "apps:list":
            return self.apps_list()

        if cmd == "config:show":
            return self.config_list(args[0])

        if cmd == "domains:report":
            return self.domains_report(args[0])