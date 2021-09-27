from typing import Union

import numpy as np
import spotpy
from spotpy.parameter import Uniform, ParameterSet
from spotpy.objectivefunctions import rmse

from src.xaj.xaj import xaj


class SpotSetup(object):
    B = Uniform(low=0.1, high=0.4)
    IM = Uniform(low=0.01, high=0.04)
    UM = Uniform(low=10, high=20)
    LM = Uniform(low=60, high=90)
    DM = Uniform(low=50, high=90)
    C = Uniform(low=0.1, high=0.2)
    SM = Uniform(low=5, high=60)
    EX = Uniform(low=1.0, high=1.5)
    KI = Uniform(low=0, high=0.7)
    KG = Uniform(low=0, high=0.7)
    CS = Uniform(low=0, high=1)
    CI = Uniform(low=0, high=0.9)
    CG = Uniform(low=0.95, high=0.998)

    def __init__(self, p_and_e, qobs, init_states, obj_func=None):
        # Just a way to keep this example flexible and applicable to various examples
        self.obj_func = obj_func
        # Load Observation data from file
        self.p_and_e = p_and_e
        self.init_states = init_states
        self.trueObs = qobs

    def simulation(self, x: ParameterSet) -> Union[list, np.array]:
        """
        run xaj model

        Parameters
        ----------
        x:
            the parameters of xaj. This function only has this one parameter.

        Returns
        -------
        list
                simulated result from xaj
        """
        # Here the model is actualy startet with one paramter combination
        sim = xaj(self.p_and_e, x, states=self.init_states)
        # The first year of simulation data is ignored (warm-up)
        return sim[0, 365:, 0]

    def evaluation(self) -> Union[list, np.array]:
        """
        read observation values

        Returns
        -------
        Union[list, np.array]
            observation
        """
        return self.trueObs[0, 365:, 0]

    def objectivefunction(self,
                          simulation: Union[list, np.array],
                          evaluation: Union[list, np.array],
                          params=None) -> float:
        """
        A user defined objective function to calculate fitness.

        Parameters
        ----------
        simulation:
            simulation results
        evaluation:
            evaluation results
        params:
            parameters leading to the simulation

        Returns
        -------
        float
            likelihood
        """
        # SPOTPY expects to get one or multiple values back,
        # that define the performance of the model run
        if not self.obj_func:
            # This is used if not overwritten by user
            like = rmse(evaluation, simulation)
        else:
            # Way to ensure flexible spot setup class
            like = self.obj_func(evaluation, simulation)
        return like


def calibrate_xaj_sceua(p_and_e, qobs, init_states, random_state=2000):
    parallel = 'seq'  # Runs everthing in sequential mode
    np.random.seed(random_state)  # Makes the results reproduceable

    # Initialize the xaj example
    # In this case, we tell the setup which algorithm we want to use, so
    # we can use this exmaple for different algorithms
    spot_setup = SpotSetup(p_and_e, qobs, init_states, spotpy.objectivefunctions.rmse)
    # Select number of maximum allowed repetitions
    sampler = spotpy.algorithms.sceua(spot_setup, dbname='SCEUA_xaj', dbformat='csv', random_state=random_state)
    rep = 5000
    # Start the sampler, one can specify ngs, kstop, peps and pcento id desired
    sampler.sample(rep, ngs=7, kstop=3, peps=0.1, pcento=0.1)
    print("Calibrate Finished!")