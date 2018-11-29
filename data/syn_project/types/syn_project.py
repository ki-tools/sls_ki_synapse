import graphene


class SynProject(graphene.ObjectType):
    """
    Defines the SynProject type.
    """
    id = graphene.String()
    name = graphene.String()

    @staticmethod
    def from_project(project):
        """
        Converts a Project to a SynProject.
        """
        return SynProject(
            id=project.id,
            name=project.name
        )
