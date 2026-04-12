class Critic:
    def validate(self, result):

        #si none->erreur
        if result is None:
            return False

        #si erreur 
        if isinstance(result, dict) and "error" in result:
            return False

        #si données vides
        if isinstance(result, dict) and len(result) == 0:
            return False

        return True
