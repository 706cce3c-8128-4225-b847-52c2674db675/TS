import numpy as np
from datetime import timedelta
import pandas as pd


class HIT:
    def __init__(self, date, T, Delta=10):
        '''
        Args
            T [int]: array of official total number of infected
            date [str]: array of strings with X_labels for T array
        '''
        self.Delta = Delta
        self.T = T

        self.date = pd.to_datetime(date)

    def get_gamma(self, delta=None, min_d=None, max_d=None):
        if delta == None:
            delta = self.Delta

        H = np.array(self.T[delta:-1] - self.T[:-(delta + 1)], dtype=np.float32)
        H[H == 0] = np.nan
        I = self.T[delta + 1:] - self.T[delta:-1]

        return self._timefilter(self.date[1:-delta], I / H, min_d, max_d)

    def get_H(self, delta=None, min_d=None, max_d=None):
        delta = self.Delta if delta is None else delta
        dates = np.hstack((self.date[1:-delta], self.date[-1] + timedelta(days=1)))
        return self._timefilter(dates, self.T[delta:] - self.T[:-delta], min_d, max_d)

    def get_TIR(self, delta=None, min_d=None, max_d=None):
        delta = self.Delta if delta is None else delta
        dates, gammas = self.get_gamma(delta)

        TIR = gammas[delta:].copy()

        for i in range(1, delta):
            TIR += gammas[delta - i:-i]

        return dates[delta:], TIR

    def get_T(self, min_d=None, max_d=None):
        return self._timefilter(self.date, np.array(self.T), min_d, max_d)

    def update_T(self, dates, gammas, delta=None):
        if delta == None:
            delta = self.Delta

        for g, day in zip(gammas, dates):

            dpdelmo = np.where(self.date==timedelta(days=delta-1) +pd .to_datetime(day))[0][0]
            dmo = np.where(self.date==timedelta(days=-1) +pd .to_datetime(day))[0][0]

            dpdel = np.where(self.date==timedelta(days=delta) +pd .to_datetime(day))[0]
            if len(dpdel) == 0:
                self.date = np.append(self.date, np.datetime64(timedelta(days=delta) + pd.to_datetime(day)) )
                self.T = np.append(self.T, self.T[dpdelmo] + g*(self.T[dpdelmo] - self.T[dmo]))
            else:
                print('update', self.T[dpdel[0]], 'with', self.T[dpdelmo] + g*(self.T[dpdelmo] - self.T[dmo]), 'at day', day)
                self.T[dpdel[0]] = self.T[dpdelmo] + g*(self.T[dpdelmo] - self.T[dmo])


    @staticmethod
    def _timefilter(dates, vals, min_d=None, max_d=None):

        assert len(dates) == len(vals), "Массивы должны иметь одинаковую длинну."

        idx = np.ones(len(dates), dtype=np.bool)

        if min_d is not None:
            idx = idx & (dates >= pd.to_datetime(min_d))
        if max_d is not None:
            idx = idx & (dates <= pd.to_datetime(max_d))

        return dates[idx], vals[idx]

    @staticmethod
    def H(d, Delta, T):
        return T[d + Delta - 1] - T[d - 1]

    @staticmethod
    def gamma(d, Delta, T):
        d1 = d + Delta
        h = T[d1 - 1] - T[d - 1]
        return (T[d1] - T[d1 - 1]) / h if h != 0 else 0

    @staticmethod
    def total_infection_rate(d, Delta, gamma):
        d1 = d + 1
        return sum(gamma[d1 - Delta:d1])

    def plot(self):
        D = self.Delta
        T = self.T
        d_last = len(T) - D

        x = self.date[:d_last]
        gamma = []
        tir = []

        for i in range(d_last):
            gamma.append(self.gamma(i, D, T))

        zeroes = [0, ] * D
        gamma_ext = [0, ] * D + gamma
        for i in range(D, d_last + D):
            tir.append(self.total_infection_rate(i, D, gamma_ext))

        return {
            'x': x,
            'TIR': tir,
        }

