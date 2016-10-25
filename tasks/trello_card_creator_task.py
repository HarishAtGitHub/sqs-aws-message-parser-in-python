from common.task.task import Task

class TrelloCardCreatorTask(Task):

    @classmethod
    def run(cls, data):
        try:
            from trollop import TrelloConnection
            import os
            conn = TrelloConnection(os.environ['TRELLO_KEY'],
                                    os.environ['TRELLO_AUTH_TOKEN'])
            board = conn.get_board(os.environ['TRELLO_BOARD_ID'])
            lists = board.lists
            for list in board.lists:
                if (list.name == os.environ['TRELLO_LIST_NAME']):
                    target_list = list
                    break
            target_list.add_card(data, data)
        except Exception as e:
            return False

        print("Trello Card creation successful")
        return True
