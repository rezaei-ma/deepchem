"""
UV Dataset loader
"""

from __future__ import division
from __future__ import unicode_literals

import os
import logging
import time

import numpy as np
import deepchem

logger = logging.getLogger(__name__)

TRAIN_URL = 'https://s3-us-west-1.amazonaws.com/deepchem.io/datasets/UV_training_disguised_combined_full.csv.gz'
VALID_URL = 'https://s3-us-west-1.amazonaws.com/deepchem.io/datasets/UV_test1_disguised_combined_full.csv.gz'
TEST_URL = 'https://s3-us-west-1.amazonaws.com/deepchem.io/datasets/UV_test2_disguised_combined_full.csv.gz'

TRAIN_FILENAME = "UV_training_disguised_combined_full.csv.gz"
VALID_FILENAME = "UV_test1_disguised_combined_full.csv.gz"
TEST_FILENAME = "UV_test2_disguised_combined_full.csv.gz"


def get_transformers(train_dataset):

  "Gets transformations applied on the dataset"

  transformers = list()

  return transformers


def gen_uv(UV_tasks, data_dir, train_dir, valid_dir, test_dir, shard_size=2000):

  """Loading the UV dataset; does not do train/test split"""

  time1 = time.time()

  train_files = os.path.join(data_dir, TRAIN_FILENAME)
  valid_files = os.path.join(data_dir, VALID_FILENAME)
  test_files = os.path.join(data_dir, TEST_FILENAME)

  # Download files if they don't exist

  if not os.path.exists(train_files):

    logger.info("Downloading training file...")
    deepchem.utils.download_url(url=TRAIN_URL, dest_dir=data_dir)
    logger.info("Training file download complete.")

    logger.info("Downloading validation file...")
    deepchem.utils.download_url(url=VALID_URL, dest_dir=data_dir)
    logger.info("Validation file download complete.")

    logger.info("Downloading test file...")
    deepchem.utils.download_url(url=TEST_URL, dest_dir=data_dir)
    logger.info("Test file download complete")

  # Featurizing datasets

  featurizer = None
  loader = deepchem.data.UserCSVLoader(tasks=UV_tasks, featurizer=featurizer)

  logger.info("Featurizing train datasets...")
  train_dataset = loader.featurize(input_files=train_files, shard_size=shard_size)
  logger.info("Train dataset featurization complete.")

  logger.info("Featurizing validation datasets...")
  valid_dataset = loader.featurize(input_files=valid_files, shard_size=shard_size)
  logger.info("Validation dataset featurization complete.")

  logger.info("Featurizing test datasets....")
  test_dataset = loader.featurize(input_files=test_files, shard_size=shard_size)
  logger.info("Test dataset featurization complete.")

  # TODO: Add missing entries removal

  # Shuffle the training data
  logger.info("Shuffling the training dataset")
  train_dataset.sparse_shuffle()

  # Apply transformations
  logger.info("Starting transformations")
  transformers = get_transformers(train_dataset)

  for transformer in transformers:
    logger.info("Performing transformations with {}".format(transformer.__class__.__name__))

    logger.info("Transforming the training dataset...")
    train_dataset = transformer.transform(train_dataset)
    logger.info("Training dataset transformation complete.")

    logger.info("Transforming the validation dataset...")
    valid_dataset = transformer.transform(valid_dataset)
    logger.info("Validation dataset transformation complete.")

    logger.info("Transforming the test dataset...")
    test_dataset = transformer.transform(test_dataset)
    logger.info("Test dataset transformation complete.")

  logger.info("Transformations complete.")
  logger.info("Moving datasets to corresponding directories")

  train_dataset.move(train_dir)
  logger.info("Train dataset moved.")

  valid_dataset.move(valid_dir)
  logger.info("Validation dataset moved.")

  test_dataset.move(test_dir)
  logger.info("Test dataset moved.")

  time2 = time.time()

  ##### TIMING ###########
  logger.info("TIMING: UV fitting took %0.3f s" %(time2-time1))

  return train_dataset, valid_dataset, test_dataset


def load_uv(shard_size=2000, featurizer=None, split=None, reload=True):

  """Load UV dataset; does not do train/test split"""

  data_dir = deepchem.utils.get_data_dir()
  data_dir = os.path.join(data_dir, "UV")

  UV_tasks = None

  if not os.path.exists(data_dir):
    os.mkdir(data_dir)

  train_dir = os.path.join(data_dir, "train_dir")
  valid_dir = os.path.join(data_dir, "valid_dir")
  test_dir = os.path.join(data_dir, "test_dir")

  if (os.path.exists(train_dir) and os.path.exists(valid_dir) and
    os.path.exists(test_dir)):

    logger.info("Reloading existing datasets")
    train_dataset = deepchem.data.DiskDataset(train_dir)
    valid_dataset = deepchem.data.DiskDataset(valid_dir)
    test_dataset = deepchem.data.DiskDataset(test_dir)

  else:
    logger.info("Featurizing datasets")
    train_dataset, valid_dataset, test_dataset = \
    gen_uv(UV_tasks=UV_tasks, data_dir=data_dir, train_dir=train_dir,
           valid_dir=valid_dir, test_dir=test_dir, shard_size=shard_size)

  transformers = get_transformers(train_dataset)

  return UV_tasks, (train_dataset, valid_dataset,
                    test_dataset), transformers
