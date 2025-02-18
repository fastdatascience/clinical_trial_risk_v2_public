from sqlmodel import SQLModel

# Set SQLModel metadata naming convention
SQLModel.metadata.naming_convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

from app.models.analysis_report.analysis_report import AnalysisReport
from app.models.document.document import Document
from app.models.module.base import Module
from app.models.subscription.currency import Currency
from app.models.subscription.subscription_attribute import SubscriptionAttribute
from app.models.subscription.subscription_module import SubscriptionModule
from app.models.subscription.subscription_type import SubscriptionType
from app.models.user.base import RefreshToken
from app.models.user.base import Role
from app.models.user.base import User
from app.models.user.user_module import UserModule
from app.models.user.user_resource_usage import ResourceType
from app.models.user.user_resource_usage import UserResourceUsage
from app.models.user.user_role import UserRole
from app.models.user.user_subscription import UserSubscription
from app.models.weight_profile.base import DocumentRunWeightProfile
from app.models.weight_profile.base import UserWeightProfile
from app.models.weight_profile.base import WeightProfile
from app.models.settings.settings import Settings
