from typing import Any
from copy import deepcopy
from aws_lambda_powertools import Logger

logger = Logger()

UNSUPPORTED_SOBJS = [
    "Scorecard",
    "ScorecardAssociation",
    "ScorecardMetric",
    "UserExternalCredential",
    "WebCartDocument",
]


def cleanup_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Cleans up records by removing unneeded fields and replacing newlines

    Args:
        records (list[dict[str, Any]]): List of records

    Returns:
        list[dict[str, Any]]: List of records with unneeded fields removed and newlines replaced
    """

    records = remove_unneeded_fields(records, ["attributes"])
    records = replace_newlines_in_dict_values(records)
    return records


def replace_newlines_in_dict_values(
    dicts: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Replaces newlines in the values of a dictionary

    Args:
        dicts (list[dict[str, Any]]): List of dictionaries

    Returns:
        list[dict[str, Any]]: List of dictionaries with newlines replaced
    """
    new_dicts = deepcopy(dicts)
    for record in new_dicts:
        for key, value in record.items():
            if isinstance(value, str):
                record[key] = value.encode("unicode_escape").decode("utf-8")
    logger.debug(f"Replaced newlines in dict values")
    return new_dicts


def remove_unneeded_fields(
    records: list[dict[str, Any]], fields: list[str]
) -> list[dict[str, Any]]:
    """Removes unneeded fields from a list of records

    Args:
        records (list[dict[str,Any]]): List of records
        fields (list[str]): List of fields to remove

    Returns:
        list[dict[str,Any]]: List of records with the specified fields removed
    """
    new_records = deepcopy(records)
    for record in new_records:
        for field in fields:
            del record[field]

    return new_records


def filter_out_sobjects(sobjs: list[str]) -> list[str]:
    """Filters out unsupported sobjects

    Args:
        sobjs (list[str]): List of sobjects

    Returns:
        list[str]: List of sobjects with unsupported sobjects removed
    """
    new_sobjs = deepcopy(sobjs)
    for u_sobj in UNSUPPORTED_SOBJS:
        if u_sobj in new_sobjs:
            new_sobjs.remove(u_sobj)
    logger.debug(f"Filtered out unsupported sobjects: {new_sobjs}")
    return new_sobjs
