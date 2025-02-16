# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import abc

from torch import Tensor


__all__ = ["TensorboardLogger"]


class Logger:
    """
    A template for loggers

    """

    def __init__(self, exp_name: str) -> None:
        self.exp_name = exp_name
        self.experiment = self._create_experiment()

    @abc.abstractmethod
    def _create_experiment(self) -> "Experiment":
        raise NotImplementedError

    @abc.abstractmethod
    def log_scalar(self, name: str, value: float, step: int = None) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def log_video(self, name: str, video: Tensor, step: int = None, **kwargs) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def log_hparams(self, cfg: "DictConfig") -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def __repr__(self) -> str:
        raise NotImplementedError


class TensorboardLogger(Logger):
    """
    Wrapper for the Tensoarboard logger.

    Args:
        exp_name (str): The name of the experiment.

    """

    def __init__(self, exp_name: str) -> None:
        super().__init__(exp_name=exp_name)
        self.log_dir = self.experiment.log_dir

        self._has_imported_moviepy = False

    def _create_experiment(self) -> "SummaryWriter":
        """
        Creates a tensorboard experiment.

        Args:
            exp_name (str): The name of the experiment.

        """
        try:
            from torch.utils.tensorboard import SummaryWriter
        except ImportError:
            raise ImportError("torch.utils.tensorboard could not be imported")

        return SummaryWriter(log_dir=self.exp_name)

    def log_scalar(self, name: str, value: float, step: int = None) -> None:
        """
        Logs a scalar value to the tensorboard.

        Args:
            name (str): The name of the scalar.
            value (float): The value of the scalar.
            step (int, optional): The step at which the scalar is logged. Defaults to None.
        """
        self.experiment.add_scalar(name, value, global_step=step)

    def log_video(self, name: str, video: Tensor, step: int = None, **kwargs) -> None:
        """
        Log videos inputs to the tensorboard.

        Args:
            name (str): The name of the video.
            video (Tensor): The video to be logged.
            step (int, optional): The step at which the video is logged. Defaults to None.
        """
        if not self._has_imported_moviepy:
            try:
                import moviepy  # noqa

                self._has_imported_moviepy = True
            except ImportError:
                raise Exception(
                    "moviepy not found, videos cannot be logged with TensorboardLogger"
                )
        self.experiment.add_video(
            tag=name,
            vid_tensor=video,
            global_step=step,
            **kwargs,
        )

    def log_hparams(self, cfg: "DictConfig") -> None:
        """
        Logs the hyperparameters of the experiment.

        Args:
            cfg (DictConfig): The configuration of the experiment.
        """
        txt = "\n\t".join([f"{k}: {val}" for k, val in sorted(vars(cfg).items())])
        self.experiment.add_text("hparams", txt)

    def __repr__(self) -> str:
        return self.experiment.__repr__()
