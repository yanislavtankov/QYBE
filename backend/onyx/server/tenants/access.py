from fastapi import Depends

from onyx.auth.permissions import require_permission
from onyx.db.enums import Permission
from onyx.db.models import User


def control_plane_dep(
    user: User = Depends(require_permission(Permission.BASIC_ACCESS)),
) -> User:
    return user
