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

import matplotlib.pyplot as plt
# import scipy.integrate as integrate
# import matplotlib.animation as animation

class ParticleBox:
    """Orbits class
    
    init_state is an [N x 4] array, where N is the number of particles:
       [[x1, y1, vx1, vy1],
        [x2, y2, vx2, vy2],
        ...               ]

    bounds is the size of the box: [xmin, xmax, ymin, ymax]
    """
    def __init__(self,
                 init_state = [[1, 0, 0, -1],
                               [-0.5, 0.5, 0.5, 0.5],
                               [-0.5, -0.5, -0.5, 0.5]],
                 bounds = [0, 4, 0, 4],
                 size = 0.04,
                 M = 0.05,
                 G = 9.8):
        self.init_state = np.array(init_state, dtype=float)
        self.M = M * np.ones(self.init_state.shape[0])
        self.size = size
        self.state = self.init_state.copy()
        self.time_elapsed = 0
        self.bounds = bounds
        self.G = G

    def step(self, dt):
        """step once by dt seconds"""
        self.time_elapsed += dt
        
        # update positions
        self.state[:, :2] += dt * self.state[:, 2:]

        # find pairs of particles undergoing a collision
        D = squareform(pdist(self.state[:, :2]))
        ind1, ind2 = np.where(D < 2 * self.size)
        unique = (ind1 < ind2)
        ind1 = ind1[unique]
        ind2 = ind2[unique]

        # update velocities of colliding pairs
        for i1, i2 in zip(ind1, ind2):
            # mass
            m1 = self.M[i1]
            m2 = self.M[i2]

            # location vector
            r1 = self.state[i1, :2]
            r2 = self.state[i2, :2]

            # velocity vector
            v1 = self.state[i1, 2:]
            v2 = self.state[i2, 2:]

            # relative location & velocity vectors
            r_rel = r1 - r2
            v_rel = v1 - v2

            # momentum vector of the center of mass
            v_cm = (m1 * v1 + m2 * v2) / (m1 + m2)

            # collisions of spheres reflect v_rel over r_rel
            rr_rel = np.dot(r_rel, r_rel)
            vr_rel = np.dot(v_rel, r_rel)
            v_rel = 2 * r_rel * vr_rel / rr_rel - v_rel

            # assign new velocities
            self.state[i1, 2:] = v_cm + v_rel * m2 / (m1 + m2)
            self.state[i2, 2:] = v_cm - v_rel * m1 / (m1 + m2) 

        # check for crossing boundary
        crossed_x1 = (self.state[:, 0] < self.bounds[0] + self.size)
        crossed_x2 = (self.state[:, 0] > self.bounds[1] - self.size)
        crossed_y1 = (self.state[:, 1] < self.bounds[2] + self.size)
        crossed_y2 = (self.state[:, 1] > self.bounds[3] - self.size)

        self.state[crossed_x1, 0] = self.bounds[0] + self.size
        self.state[crossed_x2, 0] = self.bounds[1] - self.size

        self.state[crossed_y1, 1] = self.bounds[2] + self.size
        self.state[crossed_y2, 1] = self.bounds[3] - self.size

        self.state[crossed_x1 | crossed_x2, 2] *= -1
        self.state[crossed_y1 | crossed_y2, 3] *= -1
        if (crossed_y1[0] ):
            # Crosses ground boundary
            # print "Bounce Ground"
            # print crossed_y1, crossed_y2
            return False

        # add gravity
        self.state[:, 3] -= self.M * self.G * dt
        return True


class BallGame(object):

    def __init__(self):
        #------------------------------------------------------------
        # set up initial state
        np.random.seed(0)
        init_state = -0.5 + np.random.random((50, 4))
        init_state[:, :2] *= 3.9
        
        init_state = [[0,2,1,0]]
        
        self._box = ParticleBox(init_state, size=0.04)
        self._dt = 1. / 30 # 30fps
        
        

    def reset(self):
        self._box.state[0][0] = np.random.uniform(self._box.bounds[0],self._box.bounds[1],1)[0]
        self._box.state[0][1] = self._box.bounds[2]+0.05
        self._box.state[0][3] = 0
        self._box.state[0][2] = 0
        
    def move(self, action):
        """
        action in [0,1,2,3,4,5,6,7]
        Used for initial bootstrapping
        """
        return {
            0: [-1,1],
            1: [-0.8,1],
            2: [-0.66,1],
            3: [-0.33,1],
            4: [0.0,1],
            5: [0.33,1],
            6: [0.66,1],
            7: [1,1],
            }.get(action, [-1,0]) 
        
    def init(self, U, V, Q):
        """initialize animation"""
         #------------------------------------------------------------
        # set up figure and animation
        self._fig, (self._map_ax, self._policy_ax) = plt.subplots(1, 2, sharey=False)
        # self._fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
        self._fig.set_size_inches(12.5, 6.5, forward=True)
        self._map_ax.set_title('Map')
        
        # particles holds the locations of the particles
        self._particles, = self._map_ax.plot([0,4], [0,4], 'bo', ms=4)
        self._targets, = self._map_ax.plot([], [], 'go', ms=4)
        
        # rect is the box edge
        self._rect = plt.Rectangle(self._box.bounds[::2],
                             self._box.bounds[1] - self._box.bounds[0],
                             self._box.bounds[3] - self._box.bounds[2],
                             ec='none', lw=2, fc='none')
        self._map_ax.add_patch(self._rect)
        
        self._policy_ax.set_title('Policy')
        
        scale =float(4.0)
        X,Y = np.mgrid[0:self._box.bounds[1]*scale,0:self._box.bounds[1]*scale]/float(scale)
        print X,Y
        # self._policy = self._policy_ax.quiver(X[::2, ::2],Y[::2, ::2],U[::2, ::2],V[::2, ::2], linewidth=0.5, pivot='mid', edgecolor='k', headaxislength=5, facecolor='None')
        textstr = """$\max q=%.2f$\n$\min q=%.2f$"""%(np.max(Q), np.min(Q))
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.75)
        
        # place a text box in upper left in axes coords
        self._policyText = self._policy_ax.text(0.05, 0.95, textstr, transform=self._policy_ax.transAxes, fontsize=14,
                verticalalignment='top', bbox=props)
        q_max = np.max(Q)
        q_min = np.min(Q)
        Q = (Q - q_min)/ (q_max-q_min)
        self._policy2 = self._policy_ax.quiver(X,Y,U,V,Q, alpha=.75, linewidth=1.0, pivot='mid', angles='xy', linestyles='-', scale=25.0)
        self._policy = self._policy_ax.quiver(X,Y,U,V, linewidth=0.5, pivot='mid', edgecolor='k', headaxislength=3, facecolor='None', angles='xy', linestyles='-', scale=25.0)
        
        # self._policy_ax.set_aspect(1.)
        self.setTarget(np.array([2,0]))
        
        self._particles.set_data([], [])
        self._rect.set_edgecolor('none')
        plt.ion()
        plt.show()
        return self._particles, self._rect
    
    def animate(self, i):
        """perform animation step"""
        out = self._box.step(self._dt)
    
        ms = int(self._fig.dpi * 2 * self._box.size * self._fig.get_figwidth()
                 / np.diff(self._map_ax.get_xbound())[0])
        
        # update pieces of the animation
        self._rect.set_edgecolor('k')
        self._particles.set_data(self._box.state[:, 0], self._box.state[:, 1])
        self._particles.set_markersize(ms)
        self._targets.set_data([self._target[0]], [self._target[1]])
        self._targets.set_markersize(ms)
        # return particles, rect
        return out
    
        
    def actContinuous(self, action):
        run = True
        # print "Acting: " + str(action)
        self._box.state[0][3] = action[1]
        self._box.state[0][2] = action[0]
        for i in range(500):
            run = self.animate(i)
            # print box.state
            self.update()
            
            if not run:
                return self.reward()
            
        self.reward()
            
    def reward(self):
        # More like a cost function for distance away from target
        a=(self._box.state[0,:2] - self._target)
        d = np.sqrt((a*a).sum(axis=0))
        if d < 0.3:
            return 1.0
        return 0
    
    def reward2(self):
        # More like a cost function for distance away from target
        a=(self._box.state[0,:2] - self._target)
        d = np.sqrt((a*a).sum(axis=0))
        if d < 0.3:
            return 1.0
        return -d
    
    def rewardSmooth(self, max_d):
        # More like a cost function for distance away from target
        a=(self._box.state[0,:2] - self._target)
        d = np.sqrt((a*a).sum(axis=0))
        out = 1-(d/max_d)
        return out
    
    def update(self):
        """perform animation step"""
        # update pieces of the animation
        # self._agent = self._agent + np.array([0.1,0.1])
        # print "Agent loc: " + str(self._agent)
        self._fig.canvas.draw()
        # self._line1.set_ydata(np.sin(x + phase))
        # self._fig.canvas.draw()
        
    def updatePolicy(self, U, V, Q):
                # self._policy.set_UVC(U[::2, ::2],V[::2, ::2])
        textstr = """$\max q=%.2f$\n$\min q=%.2f$"""%(np.max(Q), np.min(Q))
        self._policyText.set_text(textstr)
        q_max = np.max(Q)
        q_min = np.min(Q)
        Q = (Q - q_min)/ (q_max-q_min)
        self._policy2.set_UVC(U, V, Q)
        # self._policy2.set_vmin(1.0)
        """
        self._policy2.update_scalarmappable()
        print "cmap " + str(self._policy2.cmap)  
        print "Face colours" + str(self._policy2.get_facecolor())
        colours = ['gray','black','blue']
        cmap2 = mpl.colors.LinearSegmentedColormap.from_list('my_colormap',
                                                   colours,
                                                   256)
        self._policy2.cmap._set_extremes()
        """
        self._policy.set_UVC(U, V)
        self._fig.canvas.draw()
    
    def getState(self):
        return self._box.state[0,:2]
    
    def setState(self, st):
        self._agent = st
        self._box.state[0,0] = st[0]
        self._box.state[0,1] = st[1]
        
    def setTarget(self, st):
        self._target = st
        
    def reachedTarget(self):
        # Might be a little touchy because floats are used
        return False
    
    def finish(self):
        plt.ioff()

    def saveVisual(self, fileName):
        # plt.savefig(fileName+".svg")
        self._fig.savefig(fileName+".svg")

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
    ballGame = BallGame()
    
    ballGame.init(np.random.rand(256,1),np.random.rand(256,1),np.random.rand(256,1))
    
    for i in range(10):
        ballGame.actContinuous([1,1])
