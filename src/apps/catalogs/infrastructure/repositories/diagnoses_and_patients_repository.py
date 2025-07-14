from datetime import date
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy import delete, func, select

from src.apps.catalogs.infrastructure.api.schemas.requests.diagnoses_catalog_request_schemas import (
    AddDiagnosedPatientDiagnosisRecordRequestSchema,
    UpdateDiagnosedPatientDiagnosisRecordRequestSchema,
)
from src.apps.catalogs.infrastructure.api.schemas.responses.diagnoses_catalog_response_schemas import (
    DiagnosedPatientDiagnosisBaseResponseSchema,
)
from src.apps.catalogs.infrastructure.db_models.diagnoses_catalogue import (
    SQLAlchemyDiagnosesCatalogue,
    SQLAlchemyPatientsAndDiagnoses,
)
from src.apps.catalogs.interfaces.diagnoses_and_patients_repository_interface import (
    DiagnosedPatientDiagnosisRepositoryInterface,
)
from src.apps.catalogs.mappers import (
    map_diagnosed_patient_diagnosis_create_schema_to_db_entity,
    map_diagnosed_patient_diagnosis_db_entity_to_response_schema,
)
from src.shared.infrastructure.base import BaseRepository


class SQLAlchemyDiagnosedPatientDiagnosisRepositoryImpl(
    BaseRepository, DiagnosedPatientDiagnosisRepositoryInterface
):
    @staticmethod
    def _apply_filters_to_query(filters: Dict[str, Any], query):
        if filters.get("patient_id"):
            query = query.where(
                SQLAlchemyPatientsAndDiagnoses.patient_id == filters["patient_id"]
            )
        if filters.get("doctor_id"):
            query = query.where(
                SQLAlchemyPatientsAndDiagnoses.doctor_id == filters["doctor_id"]
            )
        if filters.get("diagnosis_code"):
            # Join to the 'cat_diagnoses' table, since the 'diagnosis_code' field is located there.
            diagnosis_code = filters["diagnosis_code"].lower()
            query = query.join(SQLAlchemyPatientsAndDiagnoses.diagnosis).where(
                func.lower(SQLAlchemyDiagnosesCatalogue.diagnosis_code)
                == diagnosis_code
            )
        if filters.get("date_diagnosed_from"):
            query = query.where(
                SQLAlchemyPatientsAndDiagnoses.date_diagnosed
                >= filters["date_diagnosed_from"]
            )
        if filters.get("date_diagnosed_to"):
            query = query.where(
                SQLAlchemyPatientsAndDiagnoses.date_diagnosed
                <= filters["date_diagnosed_to"]
            )

        return query

    async def exists_patient_diagnosis_record(
        self,
        patient_id: UUID,
        diagnosis_id: int,
        date_diagnosed: Optional[date] = None,
        exclude_id: Optional[UUID] = None,
    ) -> bool:
        query = select(SQLAlchemyPatientsAndDiagnoses).where(
            SQLAlchemyPatientsAndDiagnoses.patient_id == patient_id,
            SQLAlchemyPatientsAndDiagnoses.diagnosis_id == diagnosis_id,
        )
        if date_diagnosed is not None:
            query = query.where(
                SQLAlchemyPatientsAndDiagnoses.date_diagnosed == date_diagnosed
            )
        if exclude_id:
            query = query.where(SQLAlchemyPatientsAndDiagnoses.id != exclude_id)

        result = await self._async_db_session.execute(query)
        return result.scalar_one_or_none() is not None

    async def get_total_number_of_patients_and_diagnoses_records(self) -> int:
        query = select(func.count(SQLAlchemyPatientsAndDiagnoses.id))
        result = await self._async_db_session.execute(query)

        return result.scalar_one()

    async def get_by_id(
        self, record_id: UUID
    ) -> Optional[DiagnosedPatientDiagnosisBaseResponseSchema]:
        query = select(SQLAlchemyPatientsAndDiagnoses).where(
            SQLAlchemyPatientsAndDiagnoses.id == record_id
        )
        result = await self._async_db_session.execute(query)
        obj = result.scalar_one_or_none()
        if obj:
            return map_diagnosed_patient_diagnosis_db_entity_to_response_schema(obj)

        return None

    async def get_patient_and_diagnoses_records(
        self,
        filters: Optional[Dict[str, Any]] = None,
        page: int = 1,
        limit: int = 30,
    ) -> List[DiagnosedPatientDiagnosisBaseResponseSchema]:
        offset = (page - 1) * limit
        query = select(SQLAlchemyPatientsAndDiagnoses)

        # Filtering...
        if filters:
            query = self._apply_filters_to_query(filters=filters, query=query)

        query = query.offset(offset).limit(limit)

        result = await self._async_db_session.execute(query)
        records = result.scalars().all()

        return [
            map_diagnosed_patient_diagnosis_db_entity_to_response_schema(obj)
            for obj in records
        ]

    async def add_patient_diagnosis_record(
        self, request_dto: AddDiagnosedPatientDiagnosisRecordRequestSchema
    ) -> DiagnosedPatientDiagnosisBaseResponseSchema:
        obj: SQLAlchemyPatientsAndDiagnoses = (
            map_diagnosed_patient_diagnosis_create_schema_to_db_entity(request_dto)
        )
        self._async_db_session.add(obj)

        await self._async_db_session.flush()
        await self._async_db_session.refresh(obj)
        await self._async_db_session.commit()

        return map_diagnosed_patient_diagnosis_db_entity_to_response_schema(obj)

    async def update_patient_diagnosis_record(
        self,
        record_id: UUID,
        request_dto: UpdateDiagnosedPatientDiagnosisRecordRequestSchema,
    ) -> DiagnosedPatientDiagnosisBaseResponseSchema:
        query = select(SQLAlchemyPatientsAndDiagnoses).where(
            SQLAlchemyPatientsAndDiagnoses.id == record_id
        )
        result = await self._async_db_session.execute(query)
        obj = result.scalar_one_or_none()

        # Updating fields...
        update_data = request_dto.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(obj, key, value)

        await self._async_db_session.flush()
        await self._async_db_session.refresh(obj)
        await self._async_db_session.commit()

        return map_diagnosed_patient_diagnosis_db_entity_to_response_schema(obj)

    async def delete_by_id(self, record_id: UUID) -> None:
        query = delete(SQLAlchemyPatientsAndDiagnoses).where(
            SQLAlchemyPatientsAndDiagnoses.id == record_id
        )
        await self._async_db_session.execute(query)
        await self._async_db_session.commit()
