import graphene
from core import Synapse
from ..types import SynProject
from .permission_data_input import PermissionDataInput


class UpdateSynProject(graphene.Mutation):
    """
    Mutation for updating a SynProject.
    """
    ok = graphene.Boolean()
    syn_project = graphene.Field(lambda: SynProject)

    class Arguments:
        id = graphene.String(required=True)
        name = graphene.String()
        permissions = graphene.List(PermissionDataInput)

    def mutate(self,
               info,
               id,
               name,
               permissions):

        # Create the Project
        project = Synapse.client().get(id)

        if name:
            project.name = name

        if permissions:
            for permission in permissions:
                principal_id = permission['principal_id']
                access = permission['access']
                access_type = getattr(Synapse, '{0}_PERMS'.format(access))

                # Only add permissions, do not update permissions.
                current_perms = Synapse.client().getPermissions(project, principal_id)
                if not current_perms:
                    Synapse.client().setPermissions(
                        project,
                        principal_id,
                        accessType=access_type,
                        warn_if_inherits=False
                    )

        project = Synapse.client().store(project)
        updated_syn_project = SynProject.from_project(project)

        is_ok = True
        return UpdateSynProject(syn_project=updated_syn_project, ok=is_ok)
