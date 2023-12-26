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
    elif model == "AdaBoostRegressor":
        with open("./checkpoint/AdaBoostRegressor.pkl", "rb") as f:
            pred_model = pickle.load(f)
    elif model == "BaggingRegressor":
        with open("./checkpoint/BaggingRegressor.pkl", "rb") as f:
            pred_model = pickle.load(f)
    return pred_model


def predict(model, brand, cpu, cpu_brand_type, cpu_hz, gpu, ram_type, ram, ram_bus, storage, screen_resolution,
            screen_ratio, refresh_rate, screen_size, battery, weight
            ):
    pred_model = load_model(model)
    cate_data = {
        "Manufacturer": [brand],
        "CPU": [cpu],
        "RAM Type": [ram_type],
        "Screen Resolution": [screen_resolution],
        "GPU manufacturer": [gpu],
        "Screen Ratio": [screen_ratio]
    }
    nume_data = {
        "CPU brand modifier": [cpu_brand_type],
        "CPU Speed (GHz)": [cpu_hz],
        "RAM (GB)": [ram],
        "Bus (MHz)": [ram_bus],
        "Storage (GB)": [storage],
        "Screen Size (inch)": [screen_size],
        "Refresh Rate (Hz)": [refresh_rate],
        "Weight (kg)": [weight],
        "Battery": [battery],

    }
    cate_data = pd.DataFrame(cate_data)
    nume_data = pd.DataFrame(nume_data)
    cate_data = ohe.transform(cate_data)
    cate_data = pd.DataFrame(cate_data, columns=ohe.get_feature_names_out())
    data = pd.concat([nume_data, cate_data], axis=1)
    return round(float(np.exp(pred_model.predict(np.array(data))[0])) / 1_000_000, 2)


with gr.Blocks(theme=gr.themes.Soft(primary_hue="green")) as demo:
    # add gr title to the middle of the page
    gr.Markdown("# Laptop Price Prediction")

    with gr.Row():
        Model = gr.Dropdown(
            label="Model",
            choices=["XGBRegressor", "RandomForestRegressor", "GradientBoostingRegressor",
                     "AdaBoostRegressor", "BaggingRegressor",],
            value="XGBRegressor",
        )

        Brand = gr.Radio(
            label="Brand",
            choices=['acer', 'asus', 'dell', 'hp', 'lenovo', 'lg', 'msi'],
            value='acer'
        )

    gr.Markdown("## **CPU & GPU**")

    with gr.Row():

        CPUBrand = gr.Dropdown(label="CPU", choices=[
            "AMD Gen 4.0th", "AMD Gen 5.0th", "AMD Gen 6.0th", "AMD Gen 7.0th",
            "Intel Gen 11.0th", "Intel Gen 12.0th", "Intel Gen 13.0th"],
            value="Intel Gen 12.0th"
        )

        CPUBrandType = gr.Radio(label="CPU Type", choices=[3, 5, 7, 9], value=7)

    with gr.Row():
        CPUHz = gr.Slider(label="CPU Speed (GHz)", minimum=1.0, maximum=5.0, step=0.1, value=4.2, interactive=True)
        GPU = gr.Dropdown(label="GPU", choices=["AMD", "NVIDIA", "Intel"], value="Intel")

    gr.Markdown("## **RAM & Storage**")

    with gr.Row():
        RAMType = gr.Dropdown(
            label="RAM Type",
            choices=["DDR4", "LPDDR4", "LPDDR4X", "DDR5", "LPDDR5", "LPDDR5X"],
            value="DDR5"
        )

        RAM = gr.Radio(label="RAM (GB)", choices=[8, 16, 32, 64, 128], value=16)

    with gr.Row():
        RAMBus = gr.Slider(label="Bus (MHz)", minimum=1600, maximum=6400, step=400, value=3200, interactive=True)
        Storage = gr.Radio(label="Storage (GB)", choices=[256, 512, 1024, 2048], value=512)

    gr.Markdown("## **Screen**")

    with gr.Row():
        ScreenResolution = gr.Dropdown(label="Screen Resolution", choices=[
            "720p", "1080p", "2k", "3k", "4k"], value="1080p"
        )
        ScreenRatio = gr.Radio(label="Screen Ratio", choices=[
            "16:9", "16:10", "3:2"], value="16:9")

    with gr.Row():
        ScreenSize = gr.Radio(label="Screen Size (inch)", choices=[13, 14, 15, 16, 17], value=14)
        RefreshRate = gr.Radio(label="Refresh Rate (Hz)", choices=[60, 90, 120, 165, 144, 240], value=60)

    gr.Markdown("## **Other Features**")

    with gr.Row():
        Battery = gr.Radio(label="Battery (Wh)", choices=[40, 50, 60, 70, 80], value=60)
        Weight = gr.Radio(label="Weight (kg)", choices=[1.0, 1.5, 2.0, 2.5, 3.0], value=1.5)

    # Output Prediction
    gr.Markdown("## **Prediction**")

    with gr.Row():

        output = gr.Number(label="Prediction (Million VND)", info="Click Submit to predict")

    with gr.Row():
        submit_button = gr.Button("Submit")
        submit_button.click(fn=predict,
                            outputs=output,
                            inputs=[Model, Brand, CPUBrand, CPUBrandType, CPUHz, GPU, RAMType, RAM, RAMBus, Storage,
                                    ScreenResolution, ScreenRatio, RefreshRate, ScreenSize, Battery, Weight],
                            queue=True,
                            )
        clear_button = gr.ClearButton(components=[output], value="Clear")

if __name__ == "__main__":
    demo.launch()
