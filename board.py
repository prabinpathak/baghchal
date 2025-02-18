import turtle
from enum import Enum
from graph import Graph

class states(Enum):
    ADD_GOAT = 1
    SELECT_GOAT = 2
    MOVE_GOAT = 3
    SELECT_TIGER = 4
    MOVE_TIGER = 6
    # bagh and gaot
PLAYERS = Enum('TYPES', 'EMPTY TIGER GOAT')

class Board(turtle.Turtle):
    def __init__(self):
        self.pos_list = {}
        self.tigerStamp = "tiger.gif"
        self.goatStamp = "goat.gif"
        self.whiteStamp = "white.gif" #to cover old msg
        self.no_goats = 0
        self.X = -200
        self.Y = 200
        self.current_step = 12 #cuz leave cursor in middle of board
        self.died_goat = 0
        self.floating_pos = None
        self.game_state = states.ADD_GOAT
        super().__init__()
        self.myscreen = self.getscreen()
        self.myscreen.tracer(1,1)
        self.myscreen.bgpic("board.png") #400*400 px
        self.shape("turtle")
        self.color("red")
        self.penup()
        next_x = self.X
        next_y = self.Y
        for i in range(5):
            for j in range(5):
                self.setpos(next_x, next_y)
                key = 5 * i + j
                self.pos_list[key] = [next_x, next_y, PLAYERS.EMPTY, 0] 
                next_x = next_x + 100
            next_x = self.X
            next_y = next_y - 100
            self.myscreen.register_shape(self.tigerStamp)
            self.myscreen.register_shape(self.goatStamp)
            self.myscreen.register_shape(self.whiteStamp)


    def initial_bagh_setup(self): #tiger setup
        keys = self.pos_list.keys()
        tiger_ids = []
        self.shape(self.tigerStamp)
        for key in keys:
            if (key == 0 or key == 4 or key == 20 or key == 24):
                [x, y, _, _] = self.pos_list[key]
                self.setpos(x,y)
                s_id = self.stamp()
                self.pos_list[key] = [x,y,PLAYERS.TIGER, s_id]
        self.shape("turtle")
        [x, y, _, _] = self.pos_list[self.current_step]
        self.setpos(x,y)

    #listen for events
    def setup_key_events(self):
        self.myscreen.onkey(self.move_up, "Up")
        self.myscreen.onkey(self.move_down, "Down")
        self.myscreen.onkey(self.move_left, "Left")
        self.myscreen.onkey(self.move_right, "Right")
        self.myscreen.onkey(self.pressed_enter, "Return")
        self.myscreen.listen()

    #events Methods
    def move_up(self):
        if(self.current_step > 4):
            #print("DEBUG:1")
            self.current_step = self.current_step - 5
            [x, y, _, _] = self.pos_list[self.current_step]
            self.setpos(x,y)


    def move_down(self):
        if(self.current_step < 20):
            self.current_step = self.current_step + 5
            [x, y, _, _] = self.pos_list[self.current_step]
            self.setpos(x,y)


    def move_left(self):
        if((self.current_step > 0)):
            self.current_step = self.current_step - 1
            [x, y,_,_] = self.pos_list[self.current_step]
            self.setpos(x,y)


    def move_right(self):
        if( (self.current_step < 24)):
            #print("DEBUG:2")
            self.current_step = self.current_step + 1
            [x, y,_,_] = self.pos_list[self.current_step]
            self.setpos(x,y)


    def pressed_enter(self):
        #FSM like logic of baghchal (could be implemented as state pattern)
        #print("DEBUG:3", states.ADD_GOAT)
        if(self.died_goat>4):
            self.show_msg("game over")
            return
        if(self.game_state==states.ADD_GOAT):
            [x,y,t,_] = self.pos_list[self.current_step]
            if(t == PLAYERS.EMPTY):
                self.shape(self.goatStamp)
                s_id = self.stamp()
                self.pos_list[self.current_step] = [x,y,PLAYERS.GOAT, s_id]
                self.shape("turtle")
                self.game_state = states.SELECT_TIGER
                self.no_goats += 1

        elif(self.game_state == states.SELECT_GOAT):
            [x,y,t,i] = self.pos_list[self.current_step]
            if(t == PLAYERS.GOAT):
                self.clearstamp(i)
                [x,y,_,_] = self.pos_list[self.current_step]
                self.pos_list[self.current_step] = [x,y,PLAYERS.EMPTY,0]
                self.shape(self.goatStamp)
                self.floating_pos = self.current_step
                self.game_state = states.MOVE_GOAT

        elif(self.game_state == states.MOVE_GOAT):
            [x,y,t,_] = self.pos_list[self.current_step]
            if(t == PLAYERS.EMPTY and Graph.is_walk_valid(self.current_step, self.floating_pos)):
                s_id = self.stamp()
                self.pos_list[self.current_step] = [x,y,PLAYERS.GOAT, s_id]
                self.shape("turtle")
                self.game_state = states.SELECT_TIGER

        elif(self.game_state == states.SELECT_TIGER):
            [x,y,t,i] = self.pos_list[self.current_step]
            if(t == PLAYERS.TIGER):
                self.clearstamp(i)
                [x,y,_,_] = self.pos_list[self.current_step]
                self.pos_list[self.current_step] = [x,y,PLAYERS.EMPTY,0]
                self.shape(self.tigerStamp)
                self.floating_pos = self.current_step
                self.game_state = states.MOVE_TIGER

        elif(self.game_state == states.MOVE_TIGER):
            [x,y,t,_] = self.pos_list[self.current_step]
            if (t != PLAYERS.EMPTY):
                return
            if(Graph.is_walk_valid(self.current_step, self.floating_pos) ):
                s_id = self.stamp()
                print("tiger@walk")
                self.pos_list[self.current_step] = [x,y,PLAYERS.TIGER, s_id]
                self.shape("turtle")
            else:
                jump, g_pos = Graph.is_jump_valid(self.current_step, self.floating_pos )
                if(not jump and g_pos is  None):
                    #print(g_pos)
                    return
                [xg,yg,gt,i] = self.pos_list[g_pos]
                if(gt != PLAYERS.GOAT):
                    #print("not goat")
                    return
                self.clearstamp(i)#killing goat
                self.pos_list[g_pos] = [xg,yg,PLAYERS.EMPTY,i]
                self.died_goat = self.died_goat + 1
                s_id = self.stamp()
                self.pos_list[self.current_step] = [x,y,PLAYERS.TIGER, s_id]
                self.shape("turtle")
            print(self.no_goats)
            if(self.no_goats >= 20):
                self.game_state = states.SELECT_GOAT
            else:
                self.game_state = states.ADD_GOAT
        self.show_msg(self.game_state)
    def show_msg(self, msg):
        temp_pos = self.pos()
        temp_stamp = self.shape()
        self.hideturtle()
        self.setpos(0, 270)
        self.shape(self.whiteStamp)
        self.stamp()
        self.shape(temp_stamp)
        self.write(msg, True, align="center")
        self.setpos(temp_pos)
        self.showturtle()


def main():
    board = Board()
    board.initial_bagh_setup()
    board.setup_key_events()
    board.show_msg("Game Started, Place your goat")
    board.myscreen.mainloop()
if __name__ == "__main__":
    main()