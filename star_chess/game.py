from player import Player
from frontend import Frontend
from thread import ThreadWithReturnValue
from state.state import State


class Game():
    user: Player
    oppo: Player
    frontend: Frontend
    state: State

    def __init__(self, spec: str, user: Player, oppo: Player, frontend: Frontend):
        self.user = user
        self.oppo = oppo
        if self.user.color == self.oppo.color:
            raise ValueError()
        self.frontend = frontend
        self.state = State(spec, user.color)

    def play(self):
        self.frontend.display_init(self.state)
        self.user.game_begin()

        playing = True

        while playing:
            self.state.reset()
            self._play_round()

            user_query = ThreadWithReturnValue(target=self.user.play_again)
            oppo_query = ThreadWithReturnValue(target=self.oppo.play_again)

            user_query.start()
            oppo_query.start()

            user_response = user_query.join()
            oppo_response = oppo_query.join()

            playing = user_response and oppo_response

            if not playing:
                if user_response:
                    self.user.rematch_rejected()
                elif oppo_response:
                    self.oppo.rematch_rejected()

        self.user.game_end(self.state)
        self.frontend.display_end()
    
    def _play_round(self):
        self.user.round_begin()

        while (not self.state.is_game_over()):
            has_turn = self.user \
                if self.state.has_turn is self.user.color \
                else self.oppo
            move, resign = has_turn.get_move(self.state)
            if resign:
                self.state.resign_player(has_turn.color)
            elif move is None:
                self.state.pass_turn()
            else:
                self.state.make_move(move)
            self.frontend.display_update(
                self.state, set() if move is None else {move.fr, move.to})
        
        self.user.round_end()
