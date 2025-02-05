"""
Functions to insert default data into the database.
"""

import json
from decimal import Decimal
from typing import Callable

from sqlalchemy import select, text

from app.database import SessionLocal
from app.log_config import logger
from app.models import SubscriptionModule, SubscriptionType, Module, Currency, Role, SubscriptionAttribute, ResourceType
from app.models.subscription.subscription_type import SubscriptionDuration, SubscriptionTypeEnum
from app.models.user.role import RoleEnum
from app.models.user.user_resource_usage import ResourceTypeName
from app.models.weight_profile.base import WeightProfile


def db_create_all_extensions() -> None:
    """
    Create all extensions.
    """

    functions: dict[str, Callable] = {
        "uuid_ossp": create_extension_uuid_ossp
    }

    for name, func in functions.items():
        try:
            func()
        except (Exception,) as e:
            logger.error(f"Error creating extension {name}: {e}")


def db_insert_all_default_data() -> None:
    """
    Insert all default data into tables (if data isn't found in the table).
    """

    functions: dict[str, Callable] = {
        Currency.__tablename__: db_insert_currencies,
        Role.__tablename__: db_insert_roles,
        ResourceType.__tablename__: db_insert_resource_types,
        WeightProfile.__tablename__: db_insert_weight_profile,
        Module.__tablename__: db_insert_modules,
        SubscriptionType.__tablename__: db_insert_subscription_types,
        SubscriptionModule.__tablename__: db_insert_subscription_modules,
        SubscriptionAttribute.__tablename__: db_insert_subscription_attributes,
    }

    for name, func in functions.items():
        try:
            func()
        except (Exception,) as e:
            logger.error(f"Error inserting default data into table {name}: {e}")


def create_extension_uuid_ossp() -> None:
    """
    Create extension uuid-ossp.
    """

    with SessionLocal() as session:
        session.execute(text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";'))
        session.commit()


def db_insert_currencies() -> None:
    """
    Insert default data into table currency (if data isn't found in the table).
    """

    with SessionLocal() as session:
        info_logged = False

        # Currency codes
        currency_codes = ["USD", "GBP", "EURO"]

        # Insert records that do not exist - Check by code
        list_models_to_add: list[Currency] = []
        for currency_code in currency_codes:
            exists: bool = session.query(Currency.id).filter_by(code=currency_code).first() is not None
            if not exists:
                if not info_logged:
                    logger.info(f"Inserting default data into table {Currency.__tablename__}...")
                    info_logged = True

                currency = Currency(code=currency_code)
                list_models_to_add.append(currency)

        if list_models_to_add:
            session.add_all(list_models_to_add)
            session.commit()


def db_insert_subscription_types() -> None:
    """
    Insert default data into table subscription_type (if data isn't found in the table).
    """

    with SessionLocal() as session:
        info_logged = False

        # Get currency ID
        currency_id: int = session.exec(select(Currency.id).where(Currency.code == "USD")).first()[0]

        # Create SubscriptionType models
        subscription_types = [
            SubscriptionType(
                id=SubscriptionTypeEnum.BASIC.value,
                name=SubscriptionTypeEnum.BASIC.name,
                price=Decimal("20.00"),
                description="3 documents per day",
                duration=SubscriptionDuration.MONTHLY,
                currency_id=currency_id,
                is_unavailable=False,
            ),
            SubscriptionType(
                id=SubscriptionTypeEnum.STANDARD.value,
                name=SubscriptionTypeEnum.STANDARD.name,
                price=Decimal("45.00"),
                description="10 documents per day",
                duration=SubscriptionDuration.MONTHLY,
                currency_id=currency_id,
                is_unavailable=False,
            ),
            SubscriptionType(
                id=SubscriptionTypeEnum.PRO.value,
                name=SubscriptionTypeEnum.PRO.name,
                price=Decimal("60.00"),
                description="Unlimited",
                duration=SubscriptionDuration.MONTHLY,
                currency_id=currency_id,
                is_unavailable=False,
            ),
            SubscriptionType(
                id=SubscriptionTypeEnum.FREE.value,
                name=SubscriptionTypeEnum.FREE.name,
                price=Decimal("0.00"),
                description="1 document per day",
                duration=SubscriptionDuration.MONTHLY,
                currency_id=currency_id,
                is_unavailable=False,
            ),
            SubscriptionType(
                id=SubscriptionTypeEnum.GUEST.value,
                name=SubscriptionTypeEnum.GUEST.name,
                price=Decimal("0.00"),
                description="3 documents",
                duration=SubscriptionDuration.MONTHLY,
                currency_id=currency_id,
                is_unavailable=True,
            )
        ]

        # Insert records that do not exist - Check by id
        list_models_to_add: list[SubscriptionType] = []
        for subscription_type in subscription_types:
            exists: bool = session.query(SubscriptionType.id).filter_by(id=subscription_type.id).first() is not None
            if not exists:
                if not info_logged:
                    logger.info(f"Inserting default data into table {SubscriptionType.__tablename__}...")
                    info_logged = True

                list_models_to_add.append(subscription_type)

        if list_models_to_add:
            session.add_all(list_models_to_add)
            session.commit()


def db_insert_subscription_attributes() -> None:
    """
    Insert default data into table subscription_attribute (if data isn't found in the table).
    """

    with SessionLocal() as session:
        info_logged = False

        # Create SubscriptionAttribute models
        subscription_attributes = [
            SubscriptionAttribute(
                subscription_type_id=SubscriptionTypeEnum.BASIC.value,
                file_processing_limit=3,
                file_size=100
            ),
            SubscriptionAttribute(
                subscription_type_id=SubscriptionTypeEnum.STANDARD.value,
                file_processing_limit=10,
                file_size=100
            ),
            SubscriptionAttribute(
                subscription_type_id=SubscriptionTypeEnum.PRO.value,
                file_processing_limit=100,
                file_size=1000
            ),
            SubscriptionAttribute(
                subscription_type_id=SubscriptionTypeEnum.FREE.value,
                file_processing_limit=1,
                file_size=100
            ),
            SubscriptionAttribute(
                subscription_type_id=SubscriptionTypeEnum.GUEST.value,
                file_processing_limit=3,
                file_size=500
            )
        ]

        # Insert records that do not exist - Check by subscription_type_id
        list_models_to_add: list[SubscriptionAttribute] = []
        for subscription_attribute in subscription_attributes:
            exists: bool = session.query(SubscriptionAttribute.subscription_type_id).filter_by(
                subscription_type_id=subscription_attribute.subscription_type_id
            ).first() is not None
            if not exists:
                if not info_logged:
                    logger.info(f"Inserting default data into table {SubscriptionAttribute.__tablename__}...")
                    info_logged = True

                list_models_to_add.append(subscription_attribute)

        if list_models_to_add:
            session.add_all(list_models_to_add)
            session.commit()


def db_insert_modules() -> None:
    """
    Insert default data into table module (if data isn't found in the table).
    """

    with SessionLocal() as session:
        info_logged = False

        # Insert records that do not exist - Check by name
        list_models_to_add: list[Module] = []
        for module_name in get_module_names_list_for_db_insert():
            exists: bool = session.query(Module.id).filter_by(name=module_name).first() is not None
            if not exists:
                if not info_logged:
                    logger.info(f"Inserting default data into table {Module.__tablename__}...")
                    info_logged = True

                module = Module(name=module_name)
                list_models_to_add.append(module)

        if list_models_to_add:
            session.add_all(list_models_to_add)
            session.commit()


def db_insert_subscription_modules() -> None:
    """
    Insert default data into table subscription_module (if data isn't found in the table).
    """

    with SessionLocal() as session:
        info_logged = False

        # Get module names
        exclude_module_names = ["cancer_stage", "biobank", "adjuvant", "chemo", "radiation", "cancer_type"]
        module_names = [x for x in get_module_names_list_for_db_insert() if x not in exclude_module_names]

        # Get module IDs
        module_ids: list[int] = []
        for module_name in module_names:
            res_module_id = session.exec(select(Module.id).where(Module.name == module_name)).first()
            module_ids.append(res_module_id[0])
        module_ids.sort()

        # Get subscription type ID
        res_subscription_type_id = session.exec(
            select(SubscriptionType.id).where(SubscriptionType.name == SubscriptionTypeEnum.BASIC.name)
        ).first()
        subscription_type_id: int = res_subscription_type_id[0]

        # Insert records that do not exist - Check by subscription_type_id, module_id
        list_models_to_add: list[SubscriptionModule] = []
        for module_id in module_ids:
            exists: bool = session.query(SubscriptionModule).filter_by(
                subscription_type_id=subscription_type_id,
                module_id=module_id
            ).first() is not None
            if not exists:
                if not info_logged:
                    logger.info(f"Inserting default data into table {SubscriptionModule.__tablename__}...")
                    info_logged = True

                subscription_module = SubscriptionModule(
                    subscription_type_id=subscription_type_id,
                    module_id=module_id
                )
                list_models_to_add.append(subscription_module)

        if list_models_to_add:
            session.add_all(list_models_to_add)
            session.commit()


def db_insert_roles() -> None:
    """
    Insert default data into table role (if data isn't found in the table).
    """

    with SessionLocal() as session:
        info_logged = False

        # Insert records that do not exist - Check by id
        list_models_to_add: list[Role] = []
        for role_enum in RoleEnum:
            exists: bool = session.query(Role.id).filter_by(id=role_enum.value).first() is not None
            if not exists:
                if not info_logged:
                    logger.info(f"Inserting default data into table {Role.__tablename__}...")
                    info_logged = True

                role = Role(id=role_enum.value, name=role_enum.name)
                list_models_to_add.append(role)

        if list_models_to_add:
            session.add_all(list_models_to_add)
            session.commit()


def db_insert_resource_types() -> None:
    """
    Insert default data into table resource_type (if data isn't found in the table).
    """

    with SessionLocal() as session:
        info_logged = False

        # Insert records that do not exist - Check by name
        list_models_to_add: list[ResourceType] = []
        for resource_type_name in ResourceTypeName:
            exists: bool = session.query(ResourceType.id).filter_by(name=resource_type_name.value).first() is not None
            if not exists:
                if not info_logged:
                    logger.info(f"Inserting default data into table {ResourceType.__tablename__}...")
                    info_logged = True

                resource_type = ResourceType(name=resource_type_name.value)
                list_models_to_add.append(resource_type)

        if list_models_to_add:
            session.add_all(list_models_to_add)
            session.commit()


def db_insert_weight_profile() -> None:
    """
    Insert default data into table weight_profile (if data isn't found in the table).
    """

    with SessionLocal() as session:
        weight_profile_name = "Default Weight Profile"

        # Insert record if it doesn't exist - Check by name
        exists: bool = session.query(WeightProfile.name).filter_by(name=weight_profile_name).first() is not None
        if not exists:
            logger.info(f"Inserting default data into table {WeightProfile.__tablename__}...")

            other_default_weight_profile_exists: bool = session.query(WeightProfile.id).filter_by(
                default=True).first() is not None
            if other_default_weight_profile_exists:
                default = False
            else:
                default = True

            with open("schema/weight_schema.json", "r") as weight_schema_file:
                weight_schema: dict = json.loads(weight_schema_file.read())

            weight_profile = WeightProfile(name=weight_profile_name, weights=weight_schema, default=default)
            session.add(weight_profile)
            session.commit()


def get_module_names_list_for_db_insert() -> list[str]:
    """
    Get module names list for db insert.
    """

    return ["cancer_stage", "drug", "phase", "cancer", "condition", "country", "effect_estimate", "simulation",
            "sample_size", "sap", "num_arms", "cohort_size", "biobank", "num_sites", "duration", "num_visits",
            "num_interventions_per_visit", "num_interventions_total", "design", "consent", "randomisation",
            "control_negative", "healthy", "gender", "age", "child", "adjuvant", "placebo", "regimen", "chemo",
            "interim", "radiation", "document_type", "vaccine", "intervention_type", "cancer_type", "overnight_stay",
            "human_challenge"]
