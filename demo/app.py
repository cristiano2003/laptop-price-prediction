import gradio as gr
import pandas as pd
import numpy as np
import pickle

categorical_features = ['Manufacturer', 'CPU', 'RAM Type', "Screen Resolution"]
numerical_features = ['CPU Speed (GHz)', 'RAM (GB)', 'Bus (MHz)', 'Storage (GB)', 'CPU brand modifier',
                      'Screen Size (inch)', 'Refresh Rate (Hz)', 'Weight (kg)', 'Battery']
label = ['Price (VND)']

with open("./checkpoint/ohe.pkl", "rb") as f:
    ohe = pickle.load(f)


def load_model(model):
    if model == "XGBRegressor":
        with open("./checkpoint/XGBRegressor.pkl", "rb") as f:
            pred_model = pickle.load(f)
    elif model == "RandomForestRegressor":
        with open("./checkpoint/RandomForestRegressor.pkl", "rb") as f:
            pred_model = pickle.load(f)
    elif model == "GradientBoostingRegressor":
        with open("./checkpoint/GradientBoostingRegressor.pkl", "rb") as f:
            pred_model = pickle.load(f)
    return pred_model


def predict(brand, cpu, cpu_brand_type, cpu_hz, ram_type, ram, ram_bus,
            screen_resolution, refresh_rate, screen_size,
            storage, battery, weight, model
            ):
    pred_model = load_model(model)
    cate_data = {
        "Manufacturer": [brand],
        "CPU": [cpu],
        "RAM Type": [ram_type],
        "Screen Resolution": [screen_resolution]
    }
    nume_data = {
        "CPU Speed (GHz)": [cpu_hz],
        "RAM (GB)": [ram],
        "Bus (MHz)": [ram_bus],
        "CPU brand modifier": [cpu_brand_type],
        "Screen Size (inch)": [screen_size],
        "Refresh Rate (Hz)": [refresh_rate],
        "Storage (GB)": [storage],
        "Battery": [battery],
        "Weight (kg)": [weight]
    }
    cate_data = pd.DataFrame(cate_data)
    nume_data = pd.DataFrame(nume_data)
    cate_data = ohe.transform(cate_data)
    cate_data = pd.DataFrame(cate_data, columns=ohe.get_feature_names_out())
    data = pd.concat([cate_data, nume_data], axis=1)
    return round(float(pred_model.predict(np.array(data))[0]), 2) * 1000000


with gr.Blocks(theme=gr.themes.Soft(primary_hue="green")) as demo:
    # add gr title to the middle of the page
    gr.Markdown("# Laptop Price Prediction")

    with gr.Row():
        model = gr.Dropdown(
            label="Model",
            choices=["XGBRegressor", "RandomForestRegressor", "LinearRegression"],
            value="XGBRegressor",
        )

        Brand = gr.Radio(
            label="Brand",
            choices=['acer', 'asus', 'dell', 'hp', 'lenovo', 'lg', 'msi'],
            value='acer'
        )
    gr.Markdown("## **CPU**")
    with gr.Row():

        CPUBrand = gr.Dropdown(label="CPU", choices=[
            "AMD Gen 4.0th", "AMD Gen 5.0th", "AMD Gen 6.0th", "AMD Gen 7.0th",
            "Intel Gen 11.0th", "Intel Gen 12.0th", "Intel Gen 13.0th"],
            value="Intel Gen 12.0th"
        )
        CPUHz = gr.Slider(label="CPU Speed (GHz)", minimum=1.0, maximum=5.0, step=0.1, value=2.0, interactive=True)
        CPUBrandType = gr.Radio(label="CPU Type", choices=[3, 5, 7, 9], value=7)

    gr.Markdown("## **RAM**")
    with gr.Row():
        RAMType = gr.Dropdown(
            label="RAM Type",
            choices=["DDR4", "LPDDR4", "LPDDR4X", "DDR5", "LPDDR5", "LPDDR5X"],
            value="DDR5"
        )
        RAMBus = gr.Slider(label="Bus (MHz)", minimum=1600, maximum=6400, step=400, value=3200, interactive=True)
        RAM = gr.Radio(label="RAM (GB)", choices=[8, 16, 32, 64, 128], value=16)
    gr.Markdown("## **Screen**")
    with gr.Row():
        ScreenResolution = gr.Dropdown(
            label="Screen Resolution",
            choices=["1366x768", "1920x1080", "2560x1440"],
            value="1920x1080"
        )
        ScreenSize = gr.Radio(label="Screen Size (inch)", choices=[13.3, 14.0, 15.6, 17.3], value=15.6)
        RefreshRate = gr.Radio(label="Refresh Rate (Hz)", choices=[60, 120, 144, 240], value=60)

    gr.Markdown("## **Other Features**")
    with gr.Row():
        Battery = gr.Slider(label="Battery", minimum=40, maximum=90, value=70, step=1, interactive=True)
        Weight = gr.Slider(label="Weight (kg)", minimum=1.0, maximum=3.0, step=0.1, value=1.4, interactive=True)
        Storage = gr.Radio(label="Storage (GB)", choices=[256, 512, 1024, 2048], value=512)
    # Output Prediction
    gr.Markdown("## **Prediction**")
    with gr.Row():

        output = gr.Number(label="Prediction (VND)", info="Click Submit to predict")
    with gr.Row():
        submit_button = gr.Button("Submit")
        submit_button.click(fn=predict,
                            outputs=output,
                            inputs=[Brand, CPUBrand, CPUBrandType, CPUHz, RAMType, RAM, RAMBus,
                                    ScreenResolution, RefreshRate, ScreenSize, Storage, Battery, Weight, model
                                    ],
                            queue=True,
                            )
        clear_button = gr.ClearButton(components=[output], value="Clear")

if __name__ == "__main__":
    demo.launch(max_threads=50, debug=True, prevent_thread_lock=True, show_error=True)
