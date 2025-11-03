from ft_engineering import ft_engineering
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
import io
import matplotlib.pyplot as plt
from sklearn.model_selection import(
    KFold,
    ShuffleSplit,
    cross_val_score,
    learning_curve,
    train_test_split,
)
import numpy as np
import xgboost as xgb
import pandas as pd
import seaborn as sns
import os
def evaluation():
    
    results_df = pd.DataFrame({'Model': {48: 'xgboost', 49: 'xgboost', 50: 'xgboost', 51: 'xgboost', 52: 'xgboost', 53: 'xgboost', 54: 'xgboost', 55: 'xgboost', 56: 'xgboost', 57: 'xgboost', 58: 'xgboost', 59: 'xgboost'}, 'Data Set': {48: 'train', 49: 'train', 50: 'train', 51: 'train', 52: 'train', 53: 'train', 54: 'test', 55: 'test', 56: 'test', 57: 'test', 58: 'test', 59: 'test'}, 'Metric': {48: 'accuracy', 49: 'precision', 50: 'recall', 51: 'f1_score', 52: 'roc_auc', 53: 'casosNoTomaLicor', 54: 'accuracy', 55: 'precision', 56: 'recall', 57: 'f1_score', 58: 'roc_auc', 59: 'casosNoTomaLicor'}, 'Score': {48: 0.725786, 49: 0.603134, 50: 0.831605, 51: 0.699179, 52: 0.745825, 53: 12634.0, 54: 0.637002, 55: 0.519975, 56: 0.714286, 57: 0.601835, 58: 0.651548, 59: 3154.0}})
    metrics_to_plot = ["accuracy", "precision", "recall", "f1_score", "roc_auc","casosNoTomaLicor"]
    model = xgb.Booster()
    script_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(script_dir, "xgb_model.json")
    model.load_model(model_path)
    # Es una buena práctica guardar los nombres de las features para asegurar el orden
    model_features = model.feature_names
    df = ft_engineering()
    df.columns = [x.replace('__','_') for x in df.columns]
    X = df[model_features]
    X = xgb.DMatrix(X)
    Y = df["consume_licor"]
    y_pred = model.predict(X)
    threshold = 0.5
    y_pred= [1 if prob >= threshold else 0 for prob in y_pred]
    # Crear una figura con una cuadrícula de subplots (3 filas, 2 columnas)
    fig, axes = plt.subplots(3, 2, figsize=(30, 18))
    axes = axes.flatten() # Aplanar la matriz de ejes para iterar fácilmente
    fig.suptitle('Evaluaciones de modelo XGBoost', fontsize=30)
    # Iterar sobre cada métrica y crear un gráfico para ella
    custom_titles = {
        'precision': 'Precisión no toma licor',
        'recall': 'Recall no toma licor',
        'f1_score': 'F1 no toma licor',
        'accuracy': 'Accuracy General',
        'roc_auc': 'ROC AUC',
        'casosNoTomaLicor': 'Conteo Casos No Toma Licor'
    }
    for i, metric in enumerate(metrics_to_plot):
        ax = axes[i]
        # Filtrar el DataFrame para la métrica actual
        metric_df = results_df[results_df["Metric"] == metric]
        
        # Crear el gráfico de barras agrupado
        sns.barplot(data=metric_df, x="Model", y="Score", hue="Data Set", ax=ax, palette="cividis")
        ax.legend(fontsize=18)
        title = custom_titles.get(metric, metric.replace("_", " ").title())
        ax.set_title(title, fontsize=24)
        ax.set_xticks([])
        ax.set_ylabel("Puntuación", fontsize=18)
        ax.set_xlabel("")
        ax.tick_params(axis='x', rotation=45, labelsize=18)
        ax.tick_params(axis='y', labelsize=18)
        # Ajustar el límite del eje Y para que la comparación sea justa
        # Para ROC AUC, la escala es de 0.45 a 1.05 para ver mejor las diferencias
        if metric == 'roc_auc':
            ax.set_ylim(0.45, 1.05)
        elif metric == 'casosNoTomaLicor':
            max_no_toma = results_df[results_df["Metric"] == "casosNoTomaLicor"]["Score"].max()
            ax.set_ylim(0, max_no_toma + 5)
        else:
            ax.set_ylim(0, 1.05)

    # Ocultar el último subplot que no se usa
    if len(metrics_to_plot) < len(axes):
        axes[-1].set_visible(False)

    # Ajustar el diseño para que no se superpongan los títulos
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close(fig)
    buf.seek(0)
    
    return buf

