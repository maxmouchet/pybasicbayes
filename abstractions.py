import abc
import numpy as np
import copy

from util.stats import combinedata

# NOTE: data is always a (possibly masked) np.ndarray or list of (possibly
# masked) np.ndarrays.

################
#  Base class  #
################

class Distribution(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def rvs(self,size=[]):
        '''
        random variates (samples)
        '''
        pass

    @abc.abstractmethod
    def log_likelihood(self,x):
        '''
        log likelihood (either log probability mass function or log probability
        density function) of the ndarray x
        '''
        pass

#########################################################
#  Algorithm interfaces for inference in distributions  #
#########################################################

class GibbsSampling(Distribution):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def resample(self,data=[]):
        pass

    def copy_sample(self):
        '''
        return an object copy suitable for making lists of posterior samples
        (override this method to prevent copying shared structures into each sample)
        '''
        return copy.deepcopy(self)

    def resample_and_copy(self):
        self.resample()
        return self.copy_sample()

class MeanField(Distribution):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def expected_log_likelihood(self,x):
        pass

    @abc.abstractmethod
    def meanfieldupdate(self,data,weights):
        pass

    def get_vlb(self):
        raise NotImplementedError

class Collapsed(Distribution):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def log_marginal_likelihood(self,data):
        pass

    def log_predictive(self,newdata,olddata):
        return self.log_marginal_likelihood(combinedata((newdata,olddata))) \
                    - self.log_marginal_likelihood(olddata)

    def predictive(self,*args,**kwargs):
        return np.exp(self.log_predictive(*args,**kwargs))

class MaxLikelihood(Distribution):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def max_likelihood(self,data,weights=None):
        '''
        sets the parameters set to their maximum likelihood values given the
        (weighted) data
        '''
        pass

    def max_likelihood_constructor(cls,data,weights=None):
        '''
        creates a new instance with the parameters set to their maximum
        likelihood values and the hyperparameters set to something reasonable
        along the lines of empirical Bayes
        '''
        raise NotImplementedError

    def max_likelihood_withprior(self,data,weights=None):
        '''
        max_likelihood including prior statistics, for use with MAP EM
        '''
        raise NotImplementedError

class MAP(Distribution):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def map(self,data,weights=None):
        '''
        sets the parameters to their MAP values given the (weighted) data
        analogous to max_likelihood but includes pseudocounts
        '''
        pass

############
#  Models  #
############

# what differentiates a "model" from a "distribution" in this code is latent
# state over data: a model attaches a latent variable (like a label or state
# sequence) to data, and so it 'holds onto' data. Hence the add_data method.

class Model(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def add_data(self,data):
        pass

    @abc.abstractmethod
    def generate(self,keep=True,**kwargs):
        '''
        Like a distribution's rvs, but this also fills in latent state over
        data and keeps references to the data.
        '''
        pass

    def rvs(self,*args,**kwargs):
        return self.generate(*args,keep=False,**kwargs)[0] # 0th component is data, not latent stuff

##################################################
#  Algorithm interfaces for inference in models  #
##################################################

class ModelGibbsSampling(Model):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def resample_model(self): # TODO niter?
        pass

    def copy_sample(self):
        '''
        return an object copy suitable for making lists of posterior samples
        (override this method to prevent copying shared structures into each sample)
        '''
        return copy.deepcopy(self)

    def resample_and_copy(self):
        self.resample_model()
        return self.copy_sample()

class ModelMeanField(Model):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def meanfield_coordinate_descent_step(self):
        # returns variational lower bound after update
        pass

class _EMBase(Model):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def log_likelihood(self):
        # returns a log likelihood number on attached data
        pass

    def _EM_fit(self,method,tol=1e-1,maxiter=100):
        # NOTE: doesn't re-initialize!
        likes = []
        for itr in xrange(maxiter):
            method()
            likes.append(self.log_likelihood())
            if len(likes) > 1 and likes[-1]-likes[-2] < tol:
                return likes
        print 'WARNING: EM_fit reached maxiter of %d' % maxiter
        return likes

class ModelEM(_EMBase):
    __metaclass__ = abc.ABCMeta

    def EM_fit(self,tol=1e-1,maxiter=100):
        return self._EM_fit(self.EM_step,tol=tol,maxiter=maxiter)

    @abc.abstractmethod
    def EM_step(self):
        pass

class ModelMAPEM(_EMBase):
    __metaclass__ = abc.ABCMeta

    def MAP_EM_fit(self,tol=1e-1,maxiter=100):
        return self._EM_fit(self.MAP_EM_step,tol=tol,maxiter=maxiter)

    @abc.abstractmethod
    def MAP_EM_step(self):
        pass

