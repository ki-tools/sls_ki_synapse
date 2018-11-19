import graphene


class Rally(graphene.ObjectType):
    """
    Defines the Rally type.
    """
    synId = graphene.String()
    number = graphene.Int()
    title = graphene.String()
    rallyTeamId = graphene.Int()

    @staticmethod
    def from_project(project):
        """
        Converts a Project to a Rally.
        """
        return Rally(
            synId=project.id,
            number=project.annotations.rally[0],
            title=project.name,
            rallyTeamId=int(project.annotations.rallyTeam[0])
        )


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
