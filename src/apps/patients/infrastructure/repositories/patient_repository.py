from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from src.apps.catalogs.infrastructure.db_models.financing_sources_catalogue import (
    SQLAlchemyFinancingSourcesCatalog,
)
from src.apps.catalogs.infrastructure.db_models.patient_context_attributes_catalogue import (
    SQLAlchemyPatientContextAttributesCatalogue,
)
from src.apps.patients.domain.patient import PatientDomain
from src.apps.patients.infrastructure.db_models.patients import SQLAlchemyPatient
from src.apps.patients.interfaces.patient_repository_interface import (
    PatientRepositoryInterface,
)
from src.apps.patients.mappers import (
    map_patient_db_entity_to_domain,
    map_patient_domain_to_db_entity,
)
from src.shared.infrastructure.base import BaseRepository


class SQLAlchemyPatientRepository(BaseRepository, PatientRepositoryInterface):
    """
    SQLAlchemy repository for working with patients.
    """

    @staticmethod
    def _apply_filters_to_query(query, filters: Dict[str, Any]):
        full_name = filters.pop("patient_full_name", None)
        if isinstance(full_name, str):
            text = full_name.strip().lower()
            if text:
                query = query.where(SQLAlchemyPatient.full_name.ilike(f"%{text}%"))

        iin = filters.pop("iin", None)
        if isinstance(iin, str):
            text = iin.strip().lower()
            if text:
                query = query.where(SQLAlchemyPatient.iin.ilike(f"%{text}%"))

        for attribute, value in filters.items():
            column = getattr(SQLAlchemyPatient, attribute, None)
            if column is None or value is None:
                continue
            if hasattr(column, "type") and hasattr(column.type, "enums"):
                enum_value = value.value if isinstance(value, Enum) else value
                query = query.where(column == enum_value)
            elif isinstance(value, str):
                query = query.where(column.ilike(f"%{value}%"))
            else:
                query = query.where(column == value)

        return query

    async def get_total_number_of_patients(self) -> int:
        query = select(func.count(SQLAlchemyPatient.id))
        result = await self._async_db_session.execute(query)

        return result.scalar_one()

    async def get_by_id(self, patient_id: UUID) -> Optional[PatientDomain]:
        query = (
            select(SQLAlchemyPatient)
            .options(
                selectinload(SQLAlchemyPatient.financing_sources),
                selectinload(SQLAlchemyPatient.additional_attributes),
            )
            .where(SQLAlchemyPatient.id == patient_id)
        )
        result = await self._async_db_session.execute(query)
        db_patient = result.scalars().first()

        if not db_patient:
            return None

        return map_patient_db_entity_to_domain(db_patient)

    async def get_by_iin(self, patient_iin: str) -> Optional[PatientDomain]:
        query = (
            select(SQLAlchemyPatient)
            .options(
                selectinload(SQLAlchemyPatient.financing_sources),
                selectinload(SQLAlchemyPatient.additional_attributes),
            )
            .where(SQLAlchemyPatient.iin == patient_iin)
        )
        result = await self._async_db_session.execute(query)
        db_patient = result.scalars().first()

        if not db_patient:
            return None

        return map_patient_db_entity_to_domain(db_patient)

    async def get_patients(
        self,
        filters: Optional[Dict[str, Any]] = None,
        page: int = 1,
        limit: int = 30,
    ) -> List[PatientDomain]:
        query = select(SQLAlchemyPatient).options(
            selectinload(SQLAlchemyPatient.financing_sources),
            selectinload(SQLAlchemyPatient.additional_attributes),
        )

        if filters:
            query = self._apply_filters_to_query(query, filters)

        query = query.offset((page - 1) * limit).limit(limit)
        result = await self._async_db_session.execute(query)
        db_patients = result.scalars().all()

        return [
            map_patient_db_entity_to_domain(db_patient) for db_patient in db_patients
        ]

    async def create_patient(self, patient_domain: PatientDomain) -> PatientDomain:
        # Convert domain model to database entity
        db_patient = map_patient_domain_to_db_entity(patient_domain)

        # Load financing sources by IDs
        if patient_domain.financing_sources_ids:
            financing_sources_query = select(SQLAlchemyFinancingSourcesCatalog).where(
                SQLAlchemyFinancingSourcesCatalog.id.in_(
                    patient_domain.financing_sources_ids
                )
            )
            result = await self._async_db_session.execute(financing_sources_query)
            db_patient.financing_sources = list(result.scalars().all())

        # Load context attributes by IDs
        if patient_domain.context_attributes_ids:
            context_attrs_query = select(
                SQLAlchemyPatientContextAttributesCatalogue
            ).where(
                SQLAlchemyPatientContextAttributesCatalogue.id.in_(
                    patient_domain.context_attributes_ids
                )
            )
            result = await self._async_db_session.execute(context_attrs_query)
            db_patient.additional_attributes = list(result.scalars().all())

        # Add and flush new patient record
        self._async_db_session.add(db_patient)
        await self._async_db_session.flush()

        # Reload patient with relationships for accurate return
        reload_query = (
            select(SQLAlchemyPatient)
            .options(
                selectinload(SQLAlchemyPatient.financing_sources),
                selectinload(SQLAlchemyPatient.additional_attributes),
            )
            .where(SQLAlchemyPatient.id == db_patient.id)
        )
        result_patient = await self._async_db_session.execute(reload_query)
        reloaded_db_patient = result_patient.scalars().first()

        if reloaded_db_patient is None:
            raise ValueError("Patient not found after reload.")  # for mypy

        return map_patient_db_entity_to_domain(reloaded_db_patient)

    async def update_patient(self, patient_domain: PatientDomain) -> PatientDomain:
        # Fetch existing patient entity
        result = await self._async_db_session.execute(
            select(SQLAlchemyPatient)
            .options(
                selectinload(SQLAlchemyPatient.financing_sources),
                selectinload(SQLAlchemyPatient.additional_attributes),
            )
            .where(SQLAlchemyPatient.id == patient_domain.id)
        )
        db_patient = result.scalars().first()

        # Map domain to temp entity for JSONB conversion
        mapped_patient = map_patient_domain_to_db_entity(patient_domain)

        # Update JSONB fields with primitive data
        db_patient.attachment_data = mapped_patient.attachment_data
        db_patient.relatives = mapped_patient.relatives
        db_patient.addresses = mapped_patient.addresses
        db_patient.contact_info = mapped_patient.contact_info

        # Update scalar fields from domain
        SCALAR_FIELDS = [
            "iin",
            "first_name",
            "last_name",
            "middle_name",
            "maiden_name",
            "date_of_birth",
            "gender",
            "citizenship_id",
            "nationality_id",
            "social_status",
            "marital_status",
            "profile_status",
        ]
        for field in SCALAR_FIELDS:
            setattr(db_patient, field, getattr(patient_domain, field))

        # Refresh financing sources if IDs provided
        if patient_domain.financing_sources_ids is not None:
            if patient_domain.financing_sources_ids:
                financing_sources_query = select(
                    SQLAlchemyFinancingSourcesCatalog
                ).where(
                    SQLAlchemyFinancingSourcesCatalog.id.in_(
                        patient_domain.financing_sources_ids
                    )
                )
                result = await self._async_db_session.execute(financing_sources_query)
                db_patient.financing_sources = list(result.scalars().all())
            else:
                db_patient.financing_sources = []

        # Refresh context attributes if IDs provided
        if patient_domain.context_attributes_ids is not None:
            if patient_domain.context_attributes_ids:
                context_attrs_query = select(
                    SQLAlchemyPatientContextAttributesCatalogue
                ).where(
                    SQLAlchemyPatientContextAttributesCatalogue.id.in_(
                        patient_domain.context_attributes_ids
                    )
                )
                result = await self._async_db_session.execute(context_attrs_query)
                db_patient.additional_attributes = list(result.scalars().all())
            else:
                db_patient.additional_attributes = []

        # Flush updates and reload entity
        await self._async_db_session.flush()

        return map_patient_db_entity_to_domain(db_patient)

    async def delete_by_id(self, patient_id: UUID) -> None:
        query = select(SQLAlchemyPatient).where(SQLAlchemyPatient.id == patient_id)
        result = await self._async_db_session.execute(query)
        db_patient = result.scalars().first()

        await self._async_db_session.delete(db_patient)
        # await self._async_db_session.commit() - UOW is going to to this instead.
