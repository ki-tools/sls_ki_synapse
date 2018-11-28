import graphene


class SynapseAccessType(graphene.Enum):
    """
    Synapse permissions.
    """
    ADMIN = 'ADMIN'
    CAN_EDIT_AND_DELETE = 'CAN_EDIT_AND_DELETE'
    CAN_EDIT = 'CAN_EDIT'
    CAN_DOWNLOAD = 'CAN_DOWNLOAD'
    CAN_VIEW = 'CAN_VIEW'


class PermissionDataInput(graphene.InputObjectType):
    """
    Input class for 'permissions' data.
    """
    principal_id = graphene.String(
        required=True, description='ID of a Synapse user or team.')
    access = graphene.Field(SynapseAccessType, required=True)
