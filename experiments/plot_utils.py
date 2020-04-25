import seaborn as sns
from adaptive_CI.compute import collect
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from scipy.stats import norm
from time import time
from glob import glob
import scipy.stats as stats
from IPython.display import display, HTML
from adaptive_CI.saving import *
import pickle
from pickle import UnpicklingError
import copy
from itertools import compress
import scipy.stats as stats
import os



def read_dataframes(name):
    df_stats = pd.read_csv(f'results/{name}_stats.csv')
    df_sampleQuotas = pd.read_csv(f'results/{name}_sampleQuotas.csv')
    df_contrasts  = pd.read_csv(f'results/{name}_contrasts.csv')
    return df_stats, df_sampleQuotas, df_contrasts

def save_dataframes(name, df_stats, df_sampleQuotas, df_contrasts):
    df_stats.to_csv(f'results/{name}_stats.csv')
    df_sampleQuotas.to_csv(f'results/{name}_sampleQuotas.csv')
    df_contrasts.to_csv(f'results/{name}_contrasts.csv')


def read_files(file_name):
    files = glob(file_name)
    print(f'Found {len(files)} files.')
    results = []
    c = 0
    for file in files:
        try:
            with open(file, 'rb') as f:
                r = pickle.load(f)
            results.extend(r)
        except: # UnpicklingError:
            c += 1
            os.remove(file)
    print(f"{c} corrupted files in total, have been removed.")
    return results


def add_config(dfs, r):
    dfs = pd.concat(dfs)
    for key in r['config']:
        if key == 'truth':
            continue
        dfs[key] = r['config'][key]
    return dfs



def save_data_timepoints(data, timepoints, method, K):
    #data = data[timepoints, :]
    return pd.DataFrame({
        "time": np.tile(timepoints, K),
        "policy": np.repeat(np.arange(K), len(timepoints)),
        "value": data.flatten(order='F'),
        "method": [method] * data.size,
    })


def generate_dataframes(name):
    if os.path.exists(f'results/{name}_stats.csv'):
        return read_dataframes(name)
    results = read_files(f'results/weight_experiment_{name}*.pkl')

    CONFIG_COLS = list(results[0]['config'].keys())
    if 'truth' in CONFIG_COLS:
        CONFIG_COLS.remove('truth')
    df_stats = []
    df_sampleQuotas = []
    df_contrasts = []
    for r in results:
        K, T = r['config']['K'], r['config']['T']
        timepoints =  np.arange(0, T, T//100)
        
        # get statistics table
        tabs_stats = []
        for method, stat in r['stats'].items():
            stat = np.row_stack([stat, np.abs(stat[2])])
            tab_stats = pd.DataFrame({"statistic": ["estimate", "stderr", "bias", "coverage", "t-stat", "mse", "truth", 'abserr'] * stat.shape[1],
                                "policy": np.repeat(np.arange(K), stat.shape[0]),
                                "value":  stat.flatten(order='F'),
                                "method": [method] * stat.size})
            tabs_stats.append(tab_stats)
        
        df_stats.append(add_config(tabs_stats, r))


        # get contrast table
        tabs_contrasts = []
        for method, contrast in r['contrasts'].items():
            tabs_contrast = pd.DataFrame({"statistic":["truth",
                "estimate", "bias", "mse",
                "stderr", "t-stat", "cover"] * contrast.shape[1],
                "policy": np.repeat([f"(0,{k})" for k in np.arange(1,K)], contrast.shape[0]),
                "value": contrast.flatten(order='F'),
                "method": [method] * contrast.size,
                })
            tabs_contrasts.append(tabs_contrast)
        df_contrasts.append(add_config(tabs_contrasts, r))
        
        
        # for stablevar, get lambda(T-t)
        tabs_sampleQuotas = []
        for method, ratio in r['ratios'].items():
            sampleQuota = ratio * ((T - timepoints)[:,np.newaxis])
            tabs_sampleQuotas.append(save_data_timepoints(sampleQuota, timepoints, method, K))
            
        df_sampleQuotas.append(add_config(tabs_sampleQuotas, r)) 
        
            
            
    df_stats = pd.concat(df_stats)
    df_contrasts = pd.concat(df_contrasts)
    df_sampleQuotas = pd.concat(df_sampleQuotas)


    ### For arm values, add true standard error, relative variance, relerrors and coverage in df_stats
    df_covs = []
    confidence_level = np.array([0.9, 0.95])
    quantile = norm.ppf(0.5+confidence_level/2)
    new_stats = []
    for *config, df_cfg in df_stats.groupby([*CONFIG_COLS, 'method', 'policy']):
        true_se = np.std(df_cfg.query("statistic=='estimate'")['value'])
        df_relse = pd.DataFrame.copy(df_cfg.query("statistic=='stderr'"))
        df_relse['value'] = df_relse['value'] / true_se
        df_relse['statistic'] = 'relative SE' 

        
        df_relerror= pd.DataFrame.copy(df_cfg.query("statistic=='bias'"))
        df_relerror['value'] = np.array(df_relerror['value']) / true_se
        df_relerror['statistic'] = 'relerror'

        new_stats.extend([df_relse, df_relerror])

        df_tstat = pd.DataFrame.copy(df_cfg.query("statistic=='t-stat'"))

        for p, q in zip(confidence_level, quantile):
            df_tstat_cov = pd.DataFrame.copy(df_cfg.query("statistic=='t-stat'")) 
            df_tstat_cov['value'] = (np.abs(df_tstat_cov['value']) < q).astype(float)
            df_tstat_cov['statistic'] = f'{int(p*100)}% coverage of t-stat'
            df_tstat_cov['method'] =  np.array(df_tstat_cov['method'])[0] 

            df_covs.append(df_tstat_cov)

    df_stats = pd.concat([df_stats, *new_stats])
    df_covs = pd.concat(df_covs)

    ### For arm contrast values, add true standard error, relative variance, relerrors and coverage in df_stats
    df_contrast_covs = []
    new_contrasts = []
    for *config, df_cfg in df_contrasts.groupby([*CONFIG_COLS, 'method', 'policy']):
        true_se = np.std(df_cfg.query("statistic=='estimate'")['value'])
        
        df_relerror= pd.DataFrame.copy(df_cfg.query("statistic=='bias'"))
        df_relerror['value'] = np.array(df_relerror['value']) / true_se
        df_relerror['statistic'] = 'relerror'

        df_relse= pd.DataFrame.copy(df_cfg.query("statistic=='stderr'"))
        df_relse['value'] = df_relse['value'] / true_se 
        df_relse['statistic'] = 'relative SE' 

        new_contrasts.extend([df_relerror, df_relse])

        for p, q in zip(confidence_level, quantile):
            df_tstat_cov = pd.DataFrame.copy(df_cfg.query("statistic=='t-stat'")) 
            df_tstat_cov['value'] = (np.abs(df_tstat_cov['value']) < q).astype(float)
            df_tstat_cov['statistic'] = f'{int(p*100)}% coverage of t-stat'
            df_tstat_cov['method'] =  np.array(df_tstat_cov['method'])[0] 

            df_contrast_covs.append(df_tstat_cov)

    df_contrasts = pd.concat([df_contrasts, *new_contrasts])
    df_contrast_covs = pd.concat(df_contrast_covs)

    df_stats = pd.concat([df_stats, df_covs])
    df_contrasts = pd.concat([df_contrasts, df_contrast_covs])

    df_stats['dgp'] = name
    df_sampleQuotas['dgp'] = name
    df_contrasts['dgp'] = name
    save_dataframes(name=name, df_stats=df_stats, df_sampleQuotas=df_sampleQuotas,
            df_contrasts=df_contrasts)
    return df_stats, df_sampleQuotas, df_contrasts
            

def plot_converged_statistics(df, row_order=['mse', 'bias'],
                    col_order=[2, 0],
                    hue='method',
                   hue_order=['uniform', 'propscore', 'lvdl', 
                 'two_point'], noise_func='uniform', name=None):
    
    palette = sns.color_palette("muted")[:len(hue_order)]
    
    order = [f'nosignal_{noise_func}', f'lowSNR_{noise_func}', f'highSNR_{noise_func}']
    order_name = ['NO SIGNAL', 'LOW SNR', 'HIGH SNR']
    g = sns.catplot(x="dgp",
                y="value",
                order=order,
                hue='method',
                hue_order = hue_order,
                palette=palette,
                col="policy",
                col_order=col_order,
                row="statistic",
                row_order=row_order,
                kind="point",
                sharex=False,
                sharey='row',
                legend=False,
                legend_out=True,
                margin_titles=True,
                data=df)
    
    g.axes[0,0].clear()
    sns.pointplot(x = 'dgp',
                y="value",
                order=order,
                hue='method',
                hue_order = hue_order,
                palette=palette,
                ax=g.axes[0,0],
                data=df.query("policy==2 & statistic=='mse'"),
                estimator=lambda x: np.sqrt(np.mean(x)),
    )
    g.axes[0,0].get_legend().remove()
    g.axes[0,0].set_xlabel("")
    g.axes[0,0].set_ylabel("")
    
    g.axes[0,1].clear()
    sns.pointplot(x = 'dgp',
                y="value",
                order=order,
                hue='method',
                hue_order = hue_order,
                palette=palette,
                ax=g.axes[0,1],
                data=df.query("policy==0 & statistic=='mse'"),
                estimator=lambda x: np.sqrt(np.mean(x)),
    )
    g.axes[0,1].get_legend().remove()
    g.axes[0,1].set_xlabel("")
    g.axes[0,1].set_ylabel("")
    
    g.row_names = ['RMSE', 'bias']
    g.col_names = ['BAD ARM', 'GOOD ARM']

    for ax in g.axes.flat:
        plt.setp(ax.texts, text="")
    g.set_titles(row_template="{row_name}", col_template="{col_name}")



    for ax in g.axes.flat:
        ax.set_xticklabels(order_name)



    # Bias and absolute error
    g.axes[1,0].axhline(0, color="black", linestyle='--')
    g.axes[1,1].axhline(0, color="black", linestyle='--')
    

    handles, labels = g._legend_data.values(), g._legend_data.keys()
    g.fig.legend(labels=['uniform', 'propscore', 'constant allocation rate', 'two-point allocation rate'], 
                 handles=handles,loc='lower center',ncol=4, bbox_to_anchor= (0.55, 0.0))

    g.set_xlabels("")
    g.set_ylabels("")
    
    g.fig.tight_layout()
    g.fig.subplots_adjust(bottom=0.1)
    if name is not None:
        plt.savefig(f'figures/{name}.pdf', bbox_inches='tight')
    plt.show()

""" Normality """

def plot_hist(df_stats, noise_func='uniform', name=None):

    methods = ['uniform', 'propscore', 'lvdl', 'two_point']
    g = sns.FacetGrid(col="method",
                      row='dgp',
                      row_order=[f'nosignal_{noise_func}', f'lowSNR_{noise_func}', f'highSNR_{noise_func}'],
                      hue="statistic",
                      hue_order= ['relerror','t-stat'],
                      col_order=methods,
                      legend_out=True,
                      sharex=False,
                      sharey=True,
                      margin_titles=True,
                      data=df_stats)

    g = g.map(sns.distplot, "value", hist=False, kde=True)
    
    g.row_names = ['NO SIGNAL', 'LOW SNR', 'HIGH SNR']
    g.col_names = ['uniform', 'propscore', 'constant allocation rate', 'two point allocation rate']

    for ax in g.axes.flat:
        plt.setp(ax.texts, text="")
    g.set_titles(row_template="{row_name}", col_template="{col_name}")

    xs = np.linspace(-3, 3)
    for ax in g.axes.flatten():
        ax.plot(xs, norm.pdf(xs),label='N(0,1)', **{"color":"black", "linestyle":"--", "linewidth":2})
        ax.set_xticks([-2,2])
    handles, labels = g._legend_data.values(), g._legend_data.keys()
    g.fig.legend(labels=['relative error', 'CLT t-stat', 'N(0,1)'], 
                 loc='center',  ncol=3, bbox_to_anchor= (0.5, 0.03))
    g.set_xlabels("")
    g.set_ylabels("")
    
    g.fig.tight_layout()
    g.fig.subplots_adjust(bottom=0.1)
    if name is not None:
        plt.savefig(f'figures/{name}.pdf', bbox_inches='tight')
    plt.show()

def plot_lambda(df, noise_func='uniform'):
    g = sns.catplot(x="time",
                    y="value",
                    col="dgp",
                    col_order=[f'nosignal_{noise_func}', f'lowSNR_{noise_func}', f'highSNR_{noise_func}'],
                      kind="point",
                      row='policy',
                      row_order=[2,0],
                      hue="method",
                      sharex=False,
                      sharey=False,
                    legend=False,
                    legend_out=False,
                      margin_titles=True,
                      data=df)


    T = 20000

    g.col_names = ['NO SIGNAL', 'LOW SNR', 'HIGH SNR']
    g.row_names = ['BAD ARM', 'GOOD ARM']

    for ax in g.axes.flat:
        plt.setp(ax.texts, text="")
        ax.set_yscale('log')
        xticks = ax.get_xticks()
        ax.set_xticks([0,xticks[len(xticks)//2], xticks[-1]])
        ax.axhline(1.0, color="black", linestyle='--')
        ax.set_xticklabels([0, T//2, T])
    g.set_titles(row_template="{row_name}", col_template="{col_name}")



    g.set_xlabels("")
    g.set_ylabels("")

    g.fig.tight_layout()
    plt.savefig(f'figures/lambda_20000.pdf', bbox_inches='tight')
    plt.show()

def plot_contrast(df, row_order=['nosignal_uniform', 'highSNR_uniform'],
                  col_order=['mse', 'bias',  '90% coverage of t-stat' ],
                   hue_order=['uniform', 'propscore', 'lvdl', 'two_point'], name=None):
    
    palette = sns.color_palette("muted")[:len(hue_order)]
    g = sns.catplot(x="T",
                y="value",
                col="statistic",
                col_order=col_order,
                row="dgp",
                row_order=row_order,
                hue='method',
                hue_order = hue_order,
                palette=palette,
                kind="point",
                sharex=False,
                sharey=False,
                legend=False,
                legend_out=True,
                margin_titles=True,
                data=df)



    g.axes[0,0].clear()
    sns.pointplot(x = 'T',
                y="value",
                hue='method',
                hue_order = hue_order,
                palette=palette,
                ax=g.axes[0,0],
                data=df.query(f"statistic=='mse' & dgp=='{row_order[0]}'"),
                estimator=lambda x: np.sqrt(np.mean(x)),
    )
    g.axes[0,0].get_legend().remove()
    g.axes[0,0].set_xlabel("")
    g.axes[0,0].set_ylabel("")
    
    g.axes[1,0].clear()
    sns.pointplot(x = 'T',
                y="value",
                hue='method',
                hue_order = hue_order,
                palette=palette,
                ax=g.axes[1,0],
                data=df.query(f"statistic=='mse' & dgp=='{row_order[1]}'"),
                estimator=lambda x: np.sqrt(np.mean(x)),
    )
    g.axes[1,0].get_legend().remove()
    
    g.row_names = ['NO SIGNAL', 'HIGH SNR']
    g.col_names = ['RMSE', 'bias', '90% coverage of t-stat']

    for ax in g.axes.flat:
        plt.setp(ax.texts, text="")
    g.set_titles(row_template="{row_name}", col_template="{col_name}")
    
    

    
    g.axes[0,-1].axhline(0.90, color="black", linestyle='--')
    g.axes[1,-1].axhline(0.90, color="black", linestyle='--')
    

    # Bias and absolute error
    g.axes[0,1].axhline(0, color="black", linestyle='--')
    g.axes[1,1].axhline(0, color="black", linestyle='--')
    g.axes[0,0].axhline(0, color="black", linestyle='--')
    g.axes[1,0].axhline(0, color="black", linestyle='--')
    

    g.fig.tight_layout()
    handles, labels = g._legend_data.values(), g._legend_data.keys()
    g.fig.legend(labels=['uniform', 'propscore', 'constant allocation rate', 'two-point allocation rate'], 
                 handles=handles, loc='lower center', ncol=len(labels), bbox_to_anchor= (0.5, 0.0))

    g.set_xlabels("")
    g.set_ylabels("")
    g.fig.tight_layout()

    g.fig.subplots_adjust(bottom=0.1)
    

  
    if name is not None:
        plt.savefig(f'figures/{name}.pdf', bbox_inches='tight')
    plt.show()

def compare_with_W(df_stats, noise_func='uniform'):
    hue_order=['W-decorrelation_15', 'two_point']
    palette = sns.color_palette("muted")[:len(hue_order)]

    g = sns.catplot(x="T",
                y="value",
                hue='method',
                hue_order = hue_order,
                palette=palette,
                col="compareW",
                col_order=[f'highSNR_{noise_func}0', f'highSNR_{noise_func}2', f'nosignal_{noise_func}0'],
                row="statistic",
                row_order=['mse', '90% coverage of t-stat'],
                kind="point",
                sharex=False,
                sharey='row',
                legend=False,
                legend_out=True,
                margin_titles=True,
                data=df_stats)

    #### plot RMSE
    g.axes[0,0].clear()
    sns.pointplot(x = 'T',
                y="value",
                hue='method',
                hue_order = hue_order,
                palette=palette,
                ax=g.axes[0,0],
                data=df_stats.query(f"statistic=='mse' & compareW=='highSNR_{noise_func}0'"),
                estimator=lambda x: np.sqrt(np.mean(x)),
    )
    g.axes[0,0].get_legend().remove()
    g.axes[0,0].set_xlabel("")
    g.axes[0,0].set_ylabel("")
    
    g.axes[0,1].clear()
    sns.pointplot(x = 'T',
                y="value",
                hue='method',
                hue_order = hue_order,
                palette=palette,
                ax=g.axes[0,1],
                data=df_stats.query(f"statistic=='mse' & compareW=='highSNR_{noise_func}2'"),
                estimator=lambda x: np.sqrt(np.mean(x)),
    )
    g.axes[0,1].get_legend().remove()
    g.axes[0,1].set_xlabel("")
    g.axes[0,1].set_ylabel("")

    g.axes[0,2].clear()
    sns.pointplot(x = 'T',
                y="value",
                hue='method',
                hue_order = hue_order,
                palette=palette,
                ax=g.axes[0,2],
                data=df_stats.query(f"statistic=='mse' & compareW=='nosignal_{noise_func}0'"),
                estimator=lambda x: np.sqrt(np.mean(x)),
    )
    g.axes[0,2].get_legend().remove()
    g.axes[0,2].set_xlabel("")
    g.axes[0,2].set_ylabel("")

    # -------


    g.row_names = ['RMSE', '90% coverage of t-stat']

    g.col_names = ['GOOD ARM: HIGH SNR', 'BAD ARM: HIGN SNR', 'NO SIGNAL']

    for ax in g.axes.flat:
        plt.setp(ax.texts, text="")

    g.set_titles(row_template="{row_name}", col_template="{col_name}")


    g.axes.flat[0].axhline(0.0, color="black", linestyle='--')
    g.axes.flat[1].axhline(0.0, color="black", linestyle='--')
    g.axes.flat[2].axhline(0.0, color="black", linestyle='--')
    
    # Coverage  
    
    g.axes.flat[3].axhline(0.90, color="black", linestyle='--')
    g.axes.flat[4].axhline(0.90, color="black", linestyle='--')
    g.axes.flat[5].axhline(0.90, color="black", linestyle='--')


    handles, labels = g._legend_data.values(), g._legend_data.keys()
    g.fig.legend(labels=['W-decorrelation', 'two-point allocation rate'], 
                 handles=handles,loc='lower center', ncol=2, bbox_to_anchor= (0.5, 0.0))

    g.set_xlabels("")
    g.set_ylabels("")

    g.fig.tight_layout()
    g.fig.subplots_adjust(bottom=0.1)


    plt.savefig(f'figures/compare_W.pdf', bbox_inches='tight')
    plt.show()
