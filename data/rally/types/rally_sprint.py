import graphene


class RallySprint(graphene.ObjectType):
    """
    Defines the RallySprint type.
    """
    synId = graphene.String()
    letter = graphene.String()
    title = graphene.String()
    rallySynId = graphene.String()
    rallyNumber = graphene.Int()

    @staticmethod
    def from_project(project):
        """
        Converts a Project to a RallySprint.
        """
        return RallySprint(
            synId=project.id,
            letter=project.annotations.sprintLetter[0],
            title=project.name,
            rallySynId=project.annotations.rallyId[0],
            rallyNumber=project.annotations.rally[0]
        )
