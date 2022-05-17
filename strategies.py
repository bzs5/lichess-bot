"""
Some example strategies for people who want to create a custom, homemade bot.
And some handy classes to extend
"""
import math
import chess
from chess.engine import PlayResult
import random
from engine_wrapper import EngineWrapper
from time import time


class FillerEngine:
    """
    Not meant to be an actual engine.

    This is only used to provide the property "self.engine"
    in "MinimalEngine" which extends "EngineWrapper"
    """
    def __init__(self, main_engine, name=None):
        self.id = {
            "name": name
        }
        self.name = name
        self.main_engine = main_engine

    def __getattr__(self, method_name):
        main_engine = self.main_engine

        def method(*args, **kwargs):
            nonlocal main_engine
            nonlocal method_name
            return main_engine.notify(method_name, *args, **kwargs)

        return method


class MinimalEngine(EngineWrapper):
    """
    Subclass this to prevent a few random errors

    Even though MinimalEngine extends EngineWrapper,
    you don't have to actually wrap an engine.

    At minimum, just implement `search`,
    however you can also change other methods like
    `notify`, `first_search`, `get_time_control`, etc.
    """
    def __init__(self, commands, options, stderr, draw_or_resign, name=None, **popen_args):
        super().__init__(options, draw_or_resign)

        self.engine_name = self.__class__.__name__ if name is None else name

        self.engine = FillerEngine(self, name=self.name)
        self.engine.id = {
            "name": self.engine_name
        }

    def search(self, board, time_limit, ponder, draw_offered):
        """
        The method to be implemented in your homemade engine

        NOTE: This method must return an instance of "chess.engine.PlayResult"
        """
        raise NotImplementedError("The search method is not implemented")

    def notify(self, method_name, *args, **kwargs):
        """
        The EngineWrapper class sometimes calls methods on "self.engine".
        "self.engine" is a filler property that notifies <self>
        whenever an attribute is called.

        Nothing happens unless the main engine does something.

        Simply put, the following code is equivalent
        self.engine.<method_name>(<*args>, <**kwargs>)
        self.notify(<method_name>, <*args>, <**kwargs>)
        """
        pass


class ExampleEngine(MinimalEngine):
    pass


# Strategy names and ideas from tom7's excellent eloWorld video

class RandomMove(ExampleEngine):
    def search(self, board, *args):
        return PlayResult(random.choice(list(board.legal_moves)), None)

PAWN_VALUE = 100
KNIGHT_VALUE = 305
BISHOP_VALUE = 333
ROOK_VALUE = 563
QUEEN_VALUE = 950

# Used for alpha, beta, and mates:
MATE_VALUE = 100000
POS_MAX = 1000000
NEG_MAX = -1000000

# Tables that hold positional values for each piece.  Positive values mean a given
# square on the board is good for that piece.  The king was two tables, one for
# the endgame (when it is better to be active) and one for before (when it is better
# to be safe).
pawntable = [
    0,  0,  0,  0,  0,  0,  0,  0,
    5, 10, 10, -20, -20, 10, 10,  5,
    5, -5, -10,  0,  0, -10, -5,  5,
    0,  0,  0, 20, 20,  0,  0,  0,
    5,  5, 10, 25, 25, 10,  5,  5,
    10, 10, 20, 30, 30, 20, 10, 10,
    50, 50, 50, 50, 50, 50, 50, 50,
    100,  100,  100,  100,  100,  100,  100,  100]

knighttable = [
    -50, -40, -30, -30, -30, -30, -40, -50,
    -40, -20,  0,  5,  5,  0, -20, -40,
    -30,  5, 10, 15, 15, 10,  5, -30,
    -30,  0, 15, 20, 20, 15,  0, -30,
    -30,  5, 15, 20, 20, 15,  5, -30,
    -30,  0, 10, 15, 15, 10,  0, -30,
    -40, -20,  0,  0,  0,  0, -20, -40,
    -50, -40, -30, -30, -30, -30, -40, -50]

bishoptable = [
    -20, -10, -10, -10, -10, -10, -10, -20,
    -10,  5,  0,  0,  0,  0,  5, -10,
    -10, 10, 10, 10, 10, 10, 10, -10,
    -10,  0, 10, 10, 10, 10,  0, -10,
    -10,  5,  5, 10, 10,  5,  5, -10,
    -10,  0,  5, 10, 10,  5,  0, -10,
    -10,  0,  0,  0,  0,  0,  0, -10,
    -20, -10, -10, -10, -10, -10, -10, -20]

rooktable = [
    0,  0,  0,  5,  5,  0,  0,  0,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    5, 10, 10, 10, 10, 10, 10,  5,
    0,  0,  0,  0,  0,  0,  0,  0]

queentable = [
    -20, -10, -10, -5, -5, -10, -10, -20,
    -10,  0,  0,  0,  0,  0,  0, -10,
    -10,  5,  5,  5,  5,  5,  0, -10,
    0,  0,  5,  5,  5,  5,  0, -5,
    -5,  0,  5,  5,  5,  5,  0, -5,
    -10,  0,  5,  5,  5,  5,  0, -10,
    -10,  0,  0,  0,  0,  0,  0, -10,
    -20, -10, -10, -5, -5, -10, -10, -20]

kingtable = [
    20, 30, 10,  0,  0, 10, 30, 20,
    20, 20,  0,  0,  0,  0, 20, 20,
    -10, -20, -20, -20, -20, -20, -20, -10,
    -20, -30, -30, -40, -40, -30, -30, -20,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30]

kingtableend = [
    -50, -30, -30, -30, -30, -30, -30, -50,
    -30, -30,  0,  0,  0,  0, -30, -30,
    -30, -10, 20, 30, 30, 20, -10, -30,
    -30, -10, 30, 40, 40, 30, -10, -30,
    -30, -10, 30, 40, 40, 30, -10, -30,
    -30, -10, 20, 30, 30, 20, -10, -30,
    -30, -20, -10,  0,  0, -10, -20, -30,
    -50, -40, -30, -20, -20, -30, -40, -50]

# Function that uses the above tables, accounting for color and endgame



def positionalValue(square, piece, color, endgame):
    square = square if color else 63 - square
    if piece == chess.PAWN:
        return pawntable[square]
    if piece == chess.KNIGHT:
        return knighttable[square]
    if piece == chess.BISHOP:
        return bishoptable[square]
    if piece == chess.ROOK:
        return rooktable[square]
    if piece == chess.QUEEN:
        return queentable[square]
    if piece == chess.KING:
        return kingtableend[square] if endgame else kingtable[square]




class CS4701Bot(MinimalEngine):
    def __init__(self, commands, options, stderr, draw_or_resign, name=None, **popen_args):
        print('Init started')
        super().__init__(commands, options, stderr, draw_or_resign, name, **popen_args)
        self._maxdepth = 10
        self._board = None
        print('Initialized')

    def gen_moves_q(self):
        movelist = list(self._board.legal_moves)
        out = []
        for mv in movelist:
            if self._board.is_capture(mv):
                out.append(mv)
        return out

    def eval(self):
        # Get all the pieces
        wps = self._board.pieces(chess.PAWN, chess.WHITE)
        bps = self._board.pieces(chess.PAWN, chess.BLACK)
        wns = self._board.pieces(chess.KNIGHT, chess.WHITE)
        bns = self._board.pieces(chess.KNIGHT, chess.BLACK)
        wbs = self._board.pieces(chess.BISHOP, chess.WHITE)
        bbs = self._board.pieces(chess.BISHOP, chess.BLACK)
        wrs = self._board.pieces(chess.ROOK, chess.WHITE)
        brs = self._board.pieces(chess.ROOK, chess.BLACK)
        wqs = self._board.pieces(chess.QUEEN, chess.WHITE)
        bqs = self._board.pieces(chess.QUEEN, chess.BLACK)
        wks = self._board.pieces(chess.KING, chess.WHITE)
        bks = self._board.pieces(chess.KING, chess.BLACK)
        # Calculate material for both sides
        whitematerial = len(wns) * KNIGHT_VALUE + len(wbs) * \
            BISHOP_VALUE + len(wrs) * ROOK_VALUE + len(wqs) * QUEEN_VALUE
        blackmaterial = len(bns) * KNIGHT_VALUE + len(bbs) * \
            BISHOP_VALUE + len(brs) * ROOK_VALUE + len(bqs) * QUEEN_VALUE
        whitepawns = len(wps) * PAWN_VALUE
        blackpawns = len(wps) * PAWN_VALUE
        # Determine if we are in an endgame (useful for king tables, as well as pawn values)
        endgamew = len(wqs) == 0 or whitematerial < 1300
        endgameb = len(bqs) == 0 or blackmaterial < 1300
        endgame = endgamew and endgameb

        # Update material eval with positional eval
        whiteeval = whitematerial + whitepawns
        whiteeval += (1.5 if endgame else 1) * \
            sum([positionalValue(i, chess.PAWN, chess.WHITE, endgame)
                for i in wps])
        whiteeval += sum([positionalValue(i, chess.KNIGHT,
                         chess.WHITE, endgame) for i in wns])
        whiteeval += sum([positionalValue(i, chess.BISHOP,
                         chess.WHITE, endgame) for i in wbs])
        whiteeval += sum([positionalValue(i, chess.ROOK,
                         chess.WHITE, endgame) for i in wrs])
        whiteeval += sum([positionalValue(i, chess.QUEEN,
                         chess.WHITE, endgame) for i in wqs])
        whiteeval += sum([positionalValue(i, chess.KING,
                         chess.WHITE, endgame) for i in wks])

        # Update material eval with positional eval
        blackeval = blackmaterial + blackpawns
        blackeval += (1.5 if endgame else 1) * \
            sum([positionalValue(i, chess.PAWN, chess.BLACK, endgame)
                for i in bps])
        blackeval += sum([positionalValue(i, chess.KNIGHT,
                         chess.BLACK, endgame) for i in bns])
        blackeval += sum([positionalValue(i, chess.BISHOP,
                         chess.BLACK, endgame) for i in bbs])
        blackeval += sum([positionalValue(i, chess.ROOK,
                         chess.BLACK, endgame) for i in brs])
        blackeval += sum([positionalValue(i, chess.QUEEN,
                         chess.BLACK, endgame) for i in bqs])
        blackeval += sum([positionalValue(i, chess.KING,
                         chess.BLACK, endgame) for i in bks])

        # Final eval is difference between sides, depending on turn
        return whiteeval - blackeval if self._board.turn else blackeval - whiteeval
    
    def scoreEnd(self, depth):
        if self._board.is_check():
            return - MATE_VALUE + depth
        else:
            return 0
    
    def gen_moves(self):
        movelist = list(self._board.legal_moves)

        def heuristic(move):
            # Castling is special, so fix value
            if self._board.is_castling(move):
                return 200
            score = 0
            piece = self._board.piece_at(move.from_square).piece_type
            # Look at checks first
            if self._board.gives_check(move):
                score += 1000
            # Prioritize captures by the piece captured
            if self._board.is_capture(move):
                if piece == chess.PAWN and self._board.is_en_passant(move):
                    score += PAWN_VALUE
                else:
                    oppiece = self._board.piece_at(move.to_square).piece_type
                    if oppiece == chess.PAWN:
                        score += PAWN_VALUE
                    elif oppiece == chess.KNIGHT:
                        score += KNIGHT_VALUE
                    elif oppiece == chess.BISHOP:
                        score += BISHOP_VALUE
                    elif oppiece == chess.ROOK:
                        score += ROOK_VALUE
                    elif oppiece == chess.QUEEN:
                        score += QUEEN_VALUE
                    else:
                        # should not get here
                        pass
            # Ignore king moves to make this faster to avoid checking endgame
            if not (piece == chess.KING):
                to_pos = positionalValue(
                    move.to_square, piece, self._board.turn, False)
                from_pos = positionalValue(
                    move.from_square, piece, self._board.turn, False)
                score += (to_pos - from_pos)
            return score

        return sorted(movelist, key=heuristic, reverse=True)

    def search(self, board, time_limit, ponder, draw_offered):
       
        
        
        # try:
        #     print(str(time_limit))
        # except:
        #     pass
        EXPECTED_MOVES = 32.5
        start_time = time()
        best_eval = [0] * (self._maxdepth + 1)
        depth_time = [0] * (self._maxdepth + 1)
        best_move = [chess.Move.null()] * (self._maxdepth + 1)
        self._board = board

        # Standard alpha-beta search
        def ab_search(d, md, alpha, beta, time_lim):
            nonlocal best_move
            nonlocal best_eval
            nonlocal start_time
            nonlocal depth_time
            if d == md:
                return quiescence_search(alpha, beta)
            moves = self.gen_moves()
            if len(moves) == 0:
                return self.scoreEnd(d)

            # start the search with the previous best move
            """
            if d == 0 and not(md == 0):
                moves.remove(best_move[md-1])
                moves.insert(0, best_move[md-1])
            """

            for mv in moves:
                # if taking more than 30 seconds, return current best move 
                #print("difference in time is " + str(time() - start_time))

                # Time control area
            
                if time() - start_time >= time_lim:
                    print('inside best moves chocie thing')
                    print('bestmove: ', best_move[md])
                    break
                self._board.push(mv)
                val = -ab_search(d+1, md, - beta, -alpha, time_lim)
                self._board.pop()
                if val >= beta:
                    return beta
                if val > alpha:
                    alpha = val
                    if d == 0:
                        best_move[md] = mv
                        best_eval[md] = val
            return alpha

        # Quiesence search: check captures until we reach a quiet position
        def quiescence_search(alpha, beta):
            standpat = self.eval()
            if standpat >= beta:
                return beta
            if alpha < standpat:
                alpha = standpat
            for mv in self.gen_moves_q():
                self._board.push(mv)
                val = -quiescence_search(-beta, -alpha)
                self._board.pop()
                if val >= beta:
                    return beta
                if val > alpha:
                    alpha = val
            return alpha


        def get_c_time_left():
            if self._board.turn and time_limit.white_clock:
                # print("White")
                return time_limit.white_clock
            elif time_limit.black_clock:
                # print("Black")
                # print('time limit blackm c;lockl: ', time_limit.black_clock)
                return time_limit.black_clock
            
        base_time_left = get_c_time_left()

        if base_time_left <= 5:
            ab_search(0, 2, NEG_MAX, POS_MAX, 100000)
            return PlayResult(best_move[2], None)
        else:
            # print('time limit: ', time_limit)
            for d in range(self._maxdepth + 1):
                print("WE ARE NOW ON DEPTH " + str(d))
                # decide based on new branching factor and time taken from previous iteration if its worth it
                print()
                print("the engine had " + str(base_time_left / EXPECTED_MOVES) + " to make a move. It has ")
                if ((base_time_left / EXPECTED_MOVES) - base_time_left + get_c_time_left()) < (depth_time[d-1] * math.sqrt(len(list(self._board.legal_moves)))):
                    print("Not worth it to go the further depth. Returning move from depth " + str(d-1))
                    return PlayResult(best_move[d-1], None)

                timer_for_depth = time()
                print("Starting the timer for max depth " + str(d))
                ab_search(0, d, NEG_MAX, POS_MAX, (base_time_left / EXPECTED_MOVES))
                depth_time[d] = time() - timer_for_depth
                print("max depth " + str(d) + " took time " + str(depth_time[d]))
                if time() - start_time >= (base_time_left / EXPECTED_MOVES):
                    print("broke out of the search, returning the best move from depth " + str(d-1))
                    for i in range(d):
                        print("The best move at depth " + str(d+1) + " is " + str(best_move[i]))
                    return PlayResult(best_move[d-1], None)
            print("FINISHED THE LOOP")

        print(best_eval)
        return PlayResult(best_move[self._maxdepth], None)


        
        
      



