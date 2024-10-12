"""Main configuration for SATKIT."""

import logging
from pathlib import Path

# from icecream import ic

from .configuration_parser import (
    load_main_config, load_gui_params, load_publish_params,
    load_run_params  # , load_plot_params
)
from .configuration_classes import (
    GuiConfig, MainConfig, DataRunConfig, PublishConfig
)

_logger = logging.getLogger('satkit.configuration_setup')


class Configuration():
    """
    Main configuration class of SATKIT.
    """

    # TODO
    # - reload

    # TODO: implement an update method as well
    # as save functionality.

    # TODO: __repr__

    def __init__(
            self,
            configuration_file: Path | str | None = None
    ) -> None:
        """
        Init the main configuration object.

        Run only once. Updates should be done with methods of the class.

        Parameters
        -------
        configuration_file : Union[Path, str, None]
            Path to the main configuration file.
        """

        self._main_config_yaml = load_main_config(configuration_file)
        self._main_config = MainConfig(**self._main_config_yaml.data)

        self._data_run_yaml = load_run_params(
            self._main_config.data_run_parameter_file)
        self._data_run_config = DataRunConfig(**self._data_run_yaml.data)

        self._gui_yaml = load_gui_params(self._main_config.gui_parameter_file)
        self._gui_config = GuiConfig(**self._gui_yaml.data)

        # self._plot_yaml = load_plot_params(config['plotting_parameter_file'])
        # self._plot_config = PlotConfig(**self._plot_yaml.data)

        self._publish_yaml = load_publish_params(
            self._main_config.publish_parameter_file)
        # ic(self._publish_yaml.data)
        self._publish_config = PublishConfig(**self._publish_yaml.data)

    @property
    def main_config(self) -> MainConfig:
        """Main config options."""
        return self._main_config

    @property
    def data_run_config(self) -> DataRunConfig:
        """Config options for a data run."""
        return self._data_run_config

    @property
    def gui_config(self) -> GuiConfig:
        """Gui config options."""
        return self._gui_config

    @property
    def publish_config(self) -> PublishConfig:
        """Result publishing configuration options."""
        return self._publish_config

    def update_from_file(
            self, configuration_file: Path | str
    ) -> None:
        """
        Update the configuration from a file.

        Parameters
        ----------
        configuration_file : Union[Path, str]
            File to read the new options from.

        Raises
        ------
        NotImplementedError
            This hasn't been implemented yet.
        """
        raise NotImplementedError(
            "Updating configuration from a file has not yet been implemented.")
        # main_config.update(**config_dict)

    def save_to_file(
            self, file: Path | str
    ) -> None:
        """
        Save configuration to a file.

        Parameters
        ----------
        file : Union[Path, str]
            File to save to.

        Raises
        ------
        NotImplementedError
            This hasn't been implemented yet.
        """
        raise NotImplementedError(
            "Saving configuration to a file has not yet been implemented.")
