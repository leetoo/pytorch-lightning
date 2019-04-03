import os
import sys

from test_tube import HyperOptArgumentParser, Experiment
from pytorch-lightning.models.trainer import Trainer
from pytorch-lightning.utils.arg_parse import add_default_args
from pytorch-lightning.utils.pt_callbacks import EarlyStopping, ModelCheckpoint
from demo.example_model import ExampleModel


def main(hparams):
    """
    Main training routine specific for this project
    :param hparams:
    :return:
    """
    # init experiment
    exp = Experiment(
        name=hparams.tt_name,
        debug=hparams.debug,
        save_dir=hparams.tt_save_path,
        version=hparams.hpc_exp_number,
        autosave=False,
        description=hparams.tt_description
    )

    exp.argparse(hparams)
    exp.save()

    # build model
    model = ExampleModel(hparams)

    # callbacks
    early_stop = EarlyStopping(
        monitor='val_acc',
        patience=3,
        mode='min',
        verbose=True,
    )

    model_save_path = '{}/{}/{}'.format(hparams.model_save_path, exp.name, exp.version)
    checkpoint = ModelCheckpoint(
        filepath=model_save_path,
        save_function=None,
        save_best_only=True,
        verbose=True,
        monitor='val_acc',
        mode='min'
    )

    # configure trainer
    trainer = Trainer(
        experiment=exp,
        checkpoint_callback=checkpoint,
        early_stop_callback=early_stop,
    )

    # train model
    trainer.fit(model)


if __name__ == '__main__':

    # use default args given by lightning
    root_dir = os.path.split(os.path.dirname(sys.modules['__main__'].__file__))[0]
    parent_parser = HyperOptArgumentParser(strategy='random_search', add_help=False)
    add_default_args(parent_parser, root_dir)

    # allow model to overwrite or extend args
    parser = ExampleModel.add_model_specific_args(parent_parser)
    hyperparams = parser.parse_args()

    # train model
    main(hyperparams)
