import graphene
from .create_syn_project import CreateSynProject
from .update_syn_project import UpdateSynProject


class SynProjectMutation(graphene.ObjectType):
    """
    Defines all the SynProject mutations.
    """
    create_syn_project = CreateSynProject.Field()
    update_syn_project = UpdateSynProject.Field()
