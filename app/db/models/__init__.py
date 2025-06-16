from app.db.database import Base

# Import tất cả các model để đăng ký với Base
from .account import Account
from .action import Action
from .donation import Donation
from .Image import Image
from .permission import Permission
from .project_collaborator import ProjectCollaborator
from .project import Project
from .resource import Resource
from .role import Role
from .role_permission import RolePermissions
from .project_idea import ProjectIdea