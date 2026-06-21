"""Endpoint Smart Matchmaking.

Hanya Ketua Peneliti yang dapat mencari kolaborator (sesuai hak akses).
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.deps.auth import require_roles
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.matchmaking import MatchRequest, MatchResponse
from app.services.matchmaking import find_collaborators

router = APIRouter(prefix="/api/matchmaking", tags=["matchmaking"])


@router.post("/cari", response_model=MatchResponse)
def cari_kolaborator(
    payload: MatchRequest,
    current_user: User = Depends(require_roles(UserRole.KETUA)),
    db: Session = Depends(get_db),
) -> MatchResponse:
    """Cari kandidat kolaborator berdasarkan teks kebutuhan riset.

    Mengembalikan daftar kandidat terurut dari skor kemiripan tertinggi,
    lengkap dengan persentase skor untuk transparansi.
    """
    kandidat = find_collaborators(db, current_user.id, payload.kebutuhan_riset)
    return MatchResponse(jumlah_kandidat=len(kandidat), kandidat=kandidat)
