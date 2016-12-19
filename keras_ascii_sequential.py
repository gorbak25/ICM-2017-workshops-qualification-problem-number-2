graphics = {
    "Convolution2D": " \|/ ",
    "Activation": "|||||",
    "Flatten": "|||||",
    "MaxPooling2D": "YYYYY",
    "Dropout": " | ||",
    "Dense": "XXXXX",
    "ZeroPadding2D": "\|||/"
}

def jsonize(model):
    res = []
    for layer in model.layers:
        x = {}
        
        x["name"] = layer.name
        x["kind"] = layer.__class__.__name__
        x["input_shape"] = layer.input_shape[1:]
        x["output_shape"] = layer.output_shape[1:]
        x["n_parameters"] =  layer.count_params()
        try:
            x["activation"] = layer.activation.__name__ 
        except AttributeError:
            x["activation"] = ""
        
        res.append(x)
    return res

def compress_layers(jsonized_layers):
    res = [jsonized_layers[0]]
    for each in jsonized_layers[1:]:
        if each["kind"] == "Activation" and res[-1]["activation"] in ["", "linear"]:
            res[-1]["activation"] = each["activation"]
        else:
            res.append(each)
    return res

# data_template = "{activation:>15s}   #####   {shape} = {length}"
data_template = "{activation:>15s}   #####   {shape}"
layer_template = "{kind:>15s}   {graphics} -------------------{n_parameters:10d}   {percent_parameters:5.1f}%"

def product(iterable):
    res = 1
    for each in iterable:
        res *= each
    return res

def print_layers(jsonized_layers, sparser=False, simplify=False, header=True):
    
    if simplify:
        jsonized_layers = compress_layers(jsonized_layers)
    
    all_weights = sum([each["n_parameters"] for each in jsonized_layers])
    
    if header:
        print("      OPERATION           DATA DIMENSIONS   WEIGHTS(N)   WEIGHTS(%)\n")
    
    print(data_template.format(
            activation="Input",
            shape=jsonized_layers[0]["input_shape"],
            # length=product(jsonized_layers[0]["output_shape"])
    ))
    
    for each in jsonized_layers:
        
        if sparser:
            print("")
            
        print(layer_template.format(
                kind=each["kind"] if each["kind"] != "Activation" else "",
                graphics=graphics.get(each["kind"], "?????"),
                n_parameters=each["n_parameters"],
                percent_parameters=100 * each["n_parameters"] / all_weights
        ))
        
        if sparser:
            print("")
            
        print(data_template.format(
                activation=each["activation"] if each["activation"] != "linear" else "",
                shape=each["output_shape"],
                # length=product(each["output_shape"])
        ))
        
def sequential_model_to_ascii_printout(model, sparser=False, simplify=True, header=True):
    print_layers(jsonize(model), sparser=sparser, simplify=simplify, header=header)