from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from neo4j import AsyncDriver

from app.db.neo4j import get_neo4j_driver
from app.services import company_graph

router = APIRouter()


class CompanyResponse(BaseModel):
    id: str
    name: str
    industry: str | None = None
    connection_count: int | None = None


@router.get("/companies/search")
async def search_companies(
    q: str,
    limit: int = 10,
    driver: AsyncDriver = Depends(get_neo4j_driver),
):
    if len(q.strip()) < 2:
        return {"companies": []}
    companies = await company_graph.search_companies(driver, q, limit=min(limit, 50))
    return {"companies": companies}


@router.get("/companies/{company_id}", response_model=CompanyResponse)
async def get_company(
    company_id: str,
    driver: AsyncDriver = Depends(get_neo4j_driver),
):
    company = await company_graph.get_company(driver, company_id)
    if company is None:
        raise HTTPException(status_code=404, detail="Company not found")
    return company
