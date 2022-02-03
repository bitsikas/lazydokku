import py_cui
import py_cui.keys


class DokkuApp:
    def __init__(self, root, dokku_provider):
        self.root = root
        self.dokku_provider = dokku_provider
        self._create_app_menu()
        self._create_domains_menu()
        self._create_configs_menu()

        self.history_view = self.root.add_text_block(
            "History",
            0,
            3,
            row_span=8,
            column_span=4,
        )

        self.refresh_views()

    def _create_configs_menu(self):

        self.configs_menu = self.root.add_scroll_menu(
            "Configs",
            4,
            1,
            row_span=4,
            column_span=2,
        )
        self.configs_menu.set_border_color(py_cui.GREEN_ON_BLACK)
        self.configs_menu.set_selected_color(py_cui.BLACK_ON_GREEN)
        self.configs_menu.add_key_command(
            py_cui.keys.KEY_E_LOWER, self.edit_config
        )
        self.configs_menu.add_key_command(
            py_cui.keys.KEY_E_UPPER, self.edit_config
        )
        self.configs_menu.set_on_selection_change_event(self.show_config)

    def add_app(self, new_app=None):
        if new_app is None:
            self.root.show_text_box_popup("App", command=self.add_app)
        else:
            self.dokku_provider.add_app(new_app)
        self.refresh_apps()

    def _create_app_menu(self):
        self.apps_menu = self.root.add_scroll_menu(
            "Apps",
            0,
            0,
            row_span=8,
            column_span=1,
        )
        self.apps_menu.add_key_command(py_cui.keys.KEY_ENTER, self.add_app)
        self.apps_menu.set_border_color(py_cui.GREEN_ON_BLACK)
        self.apps_menu.set_selected_color(py_cui.BLACK_ON_GREEN)
        self.apps_menu.set_on_selection_change_event(self.refresh_views)
        self.apps_menu.add_item_list(self.dokku_provider.apps)

    def _create_domains_menu(self):

        self.domains_menu = self.root.add_scroll_menu(
            "Domains",
            0,
            1,
            row_span=4,
            column_span=2,
        )
        self.domains_menu.set_border_color(py_cui.GREEN_ON_BLACK)
        self.domains_menu.set_selected_color(py_cui.BLACK_ON_GREEN)
        self.domains_menu.add_key_command(
            py_cui.keys.KEY_ENTER, self.add_domain
        )

    def add_domain(self, new_domain=None):
        if new_domain is None:
            self.root.show_text_box_popup(
                "Domain name",
                command=self.add_domain,
            )

        else:
            self.dokku_provider.add_domain(self.selected_app, new_domain)
            self.refresh_views()

    def show_config(self):
        try:
            value = self.dokku_provider.config(self.selected_app)[
                self.configs_menu.get()
            ]
        except KeyError:
            value = ""
        self.configs_menu.set_title("Config: %s" % value)

    def edit_config(self, new_value=None):
        try:
            value = self.dokku_provider.config(self.selected_app)[
                self.configs_menu.get()
            ]
        except KeyError:
            return
        if new_value is None:
            self.root.show_text_box_popup(
                f"Change config value [{value}]", command=self.edit_config
            )
        else:

            self.dokku_provider.config(self.selected_app)[
                self.selected_config
            ] = new_value
            self.show_config()


    def refresh_apps(self):
        self.apps_menu.clear()
        self.apps_menu.add_item_list(self.dokku_provider.apps)

    def refresh_views(self):
        self.selected_app = self.apps_menu.get()
        self.selected_domain = None
        self.selected_config = None
        self.domains_menu.clear()
        self.domains_menu.set_title(
            "Domains: \u2713 %s"
            % (self.dokku_provider.letsencrypt(self.selected_app),)
        )
        self.domains_menu.add_item_list(
            self.dokku_provider.domains(self.selected_app)
        )
        self.configs_menu.clear()
        self.configs_menu.add_item_list(
            self.dokku_provider.config(self.selected_app).keys()
        )
        self.show_config()
        self.history_view.set_text(
            self.dokku_provider.executor.history
        )


def run(dokku_provider):
    # create the CUI object. Will have a 3 by 3 grid with indexes from 0,0 to 2,2
    root = py_cui.PyCUI(9, 8)

    # Add a label to the center of the CUI in the 1,1 grid position
    dokkuapp = DokkuApp(root, dokku_provider)

    # Start/Render the CUI
    root.start()
