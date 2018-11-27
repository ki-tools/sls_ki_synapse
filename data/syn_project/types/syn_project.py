import graphene


class SynProject(graphene.ObjectType):
    """
    Defines the Rally type.
    """
    id = graphene.String()
    name = graphene.String()

    @staticmethod
    def from_project(project):
        """
        Converts a Project to a Rally.
        """
        return SynProject(
            id=project.id,
            name=project.name
        )
