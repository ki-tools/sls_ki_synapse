import graphene
from core import Synapse
from ..types import SynProject


class UpdateSynProject(graphene.Mutation):
    """
    Mutation for updating a SynProject.
    """
    ok = graphene.Boolean()
    syn_project = graphene.Field(lambda: SynProject)

    class Arguments:
        id = graphene.String(required=True)
        name = graphene.String()
        participants = graphene.List(graphene.Int)

    def mutate(self,
               info,
               id,
               name,
               participants):

        # Create the Project
        project = Synapse.client().get(id)

        if name:
            project.name = name

        if participants:
            for user_id in participants:
                current_perms = Synapse.client().getPermissions(project, user_id)
                if not current_perms:
                    Synapse.client().setPermissions(
                        project,
                        user_id,
                        accessType=Synapse.CAN_EDIT_PERMS,
                        warn_if_inherits=False)

        project = Synapse.client().store(project)
        updated_syn_project = SynProject.from_project(project)

        is_ok = True
        return UpdateSynProject(syn_project=updated_syn_project, ok=is_ok)
