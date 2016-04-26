"""
Animation of Elastic collisions with Gravity

author: Jake Vanderplas
email: vanderplas@astro.washington.edu
website: http://jakevdp.github.com
license: BSD
https://jakevdp.github.io/blog/2012/08/18/matplotlib-animation-tutorial/
Please feel free to use and modify this, but keep the above information. Thanks!
"""
import numpy as np
from scipy.spatial.distance import pdist, squareform
import math
import copy
import collections

import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("Agg")
import matplotlib.animation as manimation
from BallGame1D import *
# import scipy.integrate as integrate
# import matplotlib.animation as animation


class BallGame1DChoice(BallGame1D):

    def __init__(self):
        #------------------------------------------------------------
        # set up initial state
        self._steps_forward=38
        self._choices=3
        super(BallGame1DChoice,self).__init__()
        
            
    def animate(self, i):
        """perform animation step"""
        out = super(BallGame1DChoice,self).animate(i)
        """step once by dt seconds"""
        
        # update positions
        targets_ = np.array(self._targets)
        # print "step targets: " + str(targets_)
        targets_[:,:,0] += self._dt * -1.0
        self._targets = collections.deque(list(targets_))
        scale=1.0
        ms = int(self._fig.dpi * scale * self._box.size * self._fig.get_figwidth()
                 / np.diff(self._map_ax.get_xbound())[0])
        
        self._plot_target.set_data(targets_[:,:,0].reshape((1,-1))[0], targets_[:,:,1].reshape((1,-1))[0])
        self._plot_target.set_markersize(ms)

        # return particles, rect
        return out
            
    def reset(self):
        self._box.state[0][0] = 2.0
        self._box.state[0][1] = self._box.bounds[2]+0.1
        self._box.state[0][2] = 0
        self._box.state[0][3] = (np.random.rand(1)+6.2) # think this will be about middle, y = 2.0
        self._targets = collections.deque()
        for i in range(self._steps_forward):
            self._targets.append(np.random.rand(self._choices,2))
            
        print self._targets[4]
        start_dist=2.8
        self._targets[0][:,0]=start_dist
        self._targets[0][:,1]=2.0
        for col in range(1, self._steps_forward):
            for row in range(0, self._choices):
                height = self.generateNextTarget(self._targets[col-1][row][1])
                self._targets[col][row] = [col+start_dist,height]
        self.setTargets(self._targets)
        print self._targets
        
    def resetTarget(self):
        """
        y range is [1,3]
        """
        self.resetTargets()

        
    def resetTargets(self):
        """
        y range is [1,3]
        """
        """
        val=[]
        for i in range(self._choices):
            height = self.generateNextTarget(self._targets[self._steps_forward][i,1])
            # val.append([self._targets[self._steps_forward][0,0]+1,height])
            val.append([4.0,height])
        self._targets.append(val)
        """
        self._targets.popleft()
        # self.setTargets(self._targets)
        
    def setTargets(self, st):
        """
        y range is [1,3]
        """
        self._targets=st
        
    def getStates(self):
        states=[]
        # state[0] = self._box.state[0,1]
        for i in range(self._choices):
            state = np.array([0.0,0.0], dtype=float)
            state[0] = self._targets[0][0][1] - self._previous_max_y
            state[1] = self._box.state[0,3]
            states.append(state)
        # state[2] = self._targets[0][1][1] - self._previous_max_y
        # state[3] = self._targets[0][2][1] - self._previous_max_y
        return states
    
        
    def getState(self):
        
        return self.getStates()
    
    def setState(self, st):
        self._agent = st
        self._box.state[0,0] = st[0]
        self._box.state[0,1] = st[1]
        
#ani = animation.FuncAnimation(fig, animate, frames=600,
#                               interval=10, blit=True, init_func=init)


# save the animation as an mp4.  This requires ffmpeg or mencoder to be
# installed.  The extra_args ensure that the x264 codec is used, so that
# the video can be embedded in html5.  You may need to adjust this for
# your system: for more information, see
# http://matplotlib.sourceforge.net/api/animation_api.html
#ani.save('particle_box.mp4', fps=30, extra_args=['-vcodec', 'libx264'])

# plt.show()

if __name__ == '__main__':
    
    np.random.seed(seed=10)
    ballGame = BallGame1DChoice()

    ballGame.enableRender()
    ballGame._simulate=True
    # ballGame._saveVideo=True
    print "dt: " + str(ballGame._dt)
    print "BOX: " + str(ballGame._box)
    ballGame.init(np.random.rand(16,16),np.random.rand(16,16),np.random.rand(16,16))
    
    ballGame.reset()
    ballGame.setTarget(np.array([2,2]))
    num_actions=10
    scaling = 2.0
    ballGame._box.state[0][1] = 0
    
    actions = (np.random.rand(num_actions,1)-0.5) * 2.0 * scaling
    for action in actions:
        # ballGame.resetTarget()
        state = ballGame.getState()
        # print "State: " + str(state)
        print "Action: " + str(action)
        reward = ballGame.actContinuous(action)
        print "Reward: " + str(reward)
        print "targets: " + str(ballGame._targets)
        # ballGame.resetTarget()

    ballGame.finish()