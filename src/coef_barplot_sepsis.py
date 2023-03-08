import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns

# Example values for coefs of two tasks
task_1 = "Admission to IC (AIC)"

coef_values_task_1 = [-0.14955892,0.21403687,0.8218423,-0.057706952,0.7096638,0.19789775,0.12517363,0.5200941,-0.36590415,-0.18075521,-0.3419112,0.32616827,-0.6797731,-0.04948909,-0.13667172,-0.08350992,-0.03466881,0.66938174,0.6219082,-0.14461945,-0.47652748,0.33832604,0.23330507]

static_features = ['InfectionSuspected', 'DiagnosticBlood', 'DisfuncOrg',
                       'SIRSCritTachypnea', 'Hypotensie',
                       'SIRSCritHeartRate', 'Infusion', 'DiagnosticArtAstrup', 'Age',
                       'DiagnosticIC', 'DiagnosticSputum', 'DiagnosticLiquor',
                       'DiagnosticOther', 'SIRSCriteria2OrMore', 'DiagnosticXthorax',
                       'SIRSCritTemperature', 'DiagnosticUrinaryCulture', 'SIRSCritLeucos',
                       'Oligurie', 'DiagnosticLacticAcid', 'Hypoxie',
                       'DiagnosticUrinarySediment', 'DiagnosticECG']

coefs_task_1 = dict(zip([x for x in static_features], np.array(coef_values_task_1)))

def colors_from_values(values, palette_name):
    normalized = (values - min(values)) / (max(values) - min(values))
    indices = np.round(normalized * (len(values) - 1)).astype(np.int32)
    palette = sns.color_palette(palette_name, len(values))
    return np.array(palette).take(indices, axis=0)


def my_palplot(pal, size=1, ax=None):
    n = 5
    if ax is None:
        f, ax = plt.subplots(1, 1, figsize=(n * size, size))
    ax.imshow(np.arange(n)[::-1].reshape(n, 1),
              cmap=matplotlib.colors.ListedColormap(list(pal)),
              interpolation="nearest", aspect="auto")


def plot_box_plots(coefs_1):
    matplotlib.rcParams.update({'font.size': 20, 'figure.figsize': (8,8)})
    
    max_v = max(list(coefs_1.values()))
    min_v = min(list(coefs_1.values()))
    
    fig = plt.figure(figsize=(18, 12), constrained_layout=False)
    grid = fig.add_gridspec(1, 2, width_ratios=[10, 0.2], wspace=0.2, hspace=0.0)
    
    ax1 = fig.add_subplot(grid[0, 0])
    ax2 = fig.add_subplot(grid[0, 1])
    
    def plot_on_ax(ax, coefs, title):
        coefs_values = list(coefs.values())
        coefs_names = list(coefs.keys())
        sns.barplot(x=coefs_values, y=coefs_names, orient='h', ci=0,
                    palette=colors_from_values(coefs_values, "viridis"), ax=ax)

        ax.set_xlim(min_v - 0.1*max_v, max_v + 0.1*max_v)
        ax.title.set_text(title)
    
    plot_on_ax(ax1, coefs_1, title=task_1)
    
    fig.text(0.5, 0.03, 'Value of corresponding coefficient', ha='center')

    my_palplot(sns.color_palette("viridis"), ax=ax2)
    ax2.text(-5.2, 5.0, 'Strong negative\nimpact on model\noutput')
    ax2.text(-5.2, -0.6, 'Strong positive\nimpact on model\noutput')
    ax2.set_yticks([])
    ax2.set_xticks([])
    ax2.set_xticklabels([])
    ax2.set_yticklabels([])

    plt.tight_layout()
    plt.savefig(f'../plots/coef_barplot.pdf', bbox_inches="tight")


plot_box_plots(coefs_task_1)