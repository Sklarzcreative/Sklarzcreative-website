"""Model adapters. Selected by config/flags; dry-run needs no key or network."""
from . import dryrun, openai_images, openai_review


def image_backend(no_network=False, dry_run=False):
    return dryrun if (no_network or dry_run) else openai_images


def review_backend(no_network=False, dry_run=False):
    return dryrun if (no_network or dry_run) else openai_review
