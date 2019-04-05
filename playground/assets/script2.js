import {MnistData} from './data.js';

async function getData() {
  const data = new MnistData();
  await data.load();
  console.log("Data loaded!", data);
  return data;
}

async function getModel() {
  const MODEL_URL = 'http://localhost:5000/server/model.json';
  const model = await tf.loadLayersModel(MODEL_URL);
  console.log("Model loaded!", model);
  return model;
}

function getOptimizationData() {
  // TODO: Check that the optimizer is valid.
  return {
    'optimizer_config': {
      'class_name': 'SGD',
      'config': {
        'lr': 0.0010000000474974513,
        'momentum': 0.0,
        'decay': 0.0,
        'nesterov': false
      }
    },
   'loss': 'sparse_categorical_crossentropy',
   'metrics': ['accuracy'],
   'sample_weight_mode': null,
   'loss_weights': null
 }
}

function compileModel(model, optimization_data) {

  let optimizer;
  if (optimization_data['optimizer_config']['class_name'] == 'SGD') {
    // SGD
    optimizer = tf.train.sgd(optimization_data['optimizer_config']['config']['lr']);
  } else {
    // Not supported!
    throw "Optimizer not supported!"
  }

  model.compile({
    optimizer: optimizer,
    loss: _lowerCaseToCamelCase(optimization_data['loss']),
    metrics: optimization_data['metrics'],
  });

  console.log("Model compiled!", model);
  return model;
}

async function getValidationAccuracy(model, data) {
  const [labels, preds] = await _evaluateModel(model, data);
  const accuracy = await tf.equal(preds, labels).sum().dataSync()[0] / tf.equal(preds, labels).size;
  console.log("Accuracy calculated! ", accuracy)
  return accuracy;
}

async function retrainModel(model, data) {
  const metrics = ['loss', 'acc'];

  const BATCH_SIZE = 128;
  const TRAIN_DATA_SIZE = 8000;
  //const TEST_DATA_SIZE = 1000;

  const [trainXs, trainYs] = tf.tidy(() => {
    const d = data.nextTrainBatch(TRAIN_DATA_SIZE);
    return [
      d.xs.reshape([TRAIN_DATA_SIZE, 784]),
      d.labels.argMax([-1])
    ];
  });

  // const [testXs, testYs] = tf.tidy(() => {
  //   const d = data.nextTestBatch(TEST_DATA_SIZE);
  //   return [
  //     d.xs.reshape([TEST_DATA_SIZE, 784]),
  //     d.labels.argMax([-1])
  //   ];
  // });

  return model.fit(trainXs, trainYs, {
    batchSize: BATCH_SIZE,
    // validationData: [testXs, testYs],
    epochs: 5,
    shuffle: true,
  });
}

async function _evaluateModel(model, data) {
  const IMAGE_WIDTH = 28;
  const IMAGE_HEIGHT = 28;
  const TEST_DATA_SIZE = data.testIndices.length;
  //const TEST_DATA_SIZE = 100;
  const testData = data.nextTestBatch(TEST_DATA_SIZE);
  const testxs = testData.xs.reshape([TEST_DATA_SIZE, IMAGE_WIDTH * IMAGE_HEIGHT]);
  const labels = testData.labels.argMax([-1]);
  const preds = model.predict(testxs).argMax([-1]);

  testxs.dispose();

  console.log("Model evaluated!");
  return [labels, preds];
}

// function makeModel() {
//   const model = tf.sequential();
//
//   const IMAGE_WIDTH = 28;
//   const IMAGE_HEIGHT = 28;
//   const IMAGE_CHANNELS = 1;
//
//   // In the first layer of out convolutional neural network we have
//   // to specify the input shape. Then we specify some paramaters for
//   // the convolution operation that takes place in this layer.
//   model.add(tf.layers.conv2d({
//     inputShape: [IMAGE_WIDTH, IMAGE_HEIGHT, IMAGE_CHANNELS],
//     kernelSize: 5,
//     filters: 8,
//     strides: 1,
//     activation: 'relu',
//     kernelInitializer: 'varianceScaling'
//   }));
//
//   // The MaxPooling layer acts as a sort of downsampling using max values
//   // in a region instead of averaging.
//   model.add(tf.layers.maxPooling2d({poolSize: [2, 2], strides: [2, 2]}));
//
//   // Repeat another conv2d + maxPooling stack.
//   // Note that we have more filters in the convolution.
//   model.add(tf.layers.conv2d({
//     kernelSize: 5,
//     filters: 16,
//     strides: 1,
//     activation: 'relu',
//     kernelInitializer: 'varianceScaling'
//   }));
//   model.add(tf.layers.maxPooling2d({poolSize: [2, 2], strides: [2, 2]}));
//
//   // Now we flatten the output from the 2D filters into a 1D vector to prepare
//   // it for input into our last layer. This is common practice when feeding
//   // higher dimensional data to a final classification output layer.
//   model.add(tf.layers.flatten());
//
//   // Our last layer is a dense layer which has 10 output units, one for each
//   // output class (i.e. 0, 1, 2, 3, 4, 5, 6, 7, 8, 9).
//   const NUM_OUTPUT_CLASSES = 10;
//   model.add(tf.layers.dense({
//     units: NUM_OUTPUT_CLASSES,
//     kernelInitializer: 'varianceScaling',
//     activation: 'softmax'
//   }));
//
//
//   // Choose an optimizer, loss function and accuracy metric,
//   // then compile and return the model
//   const optimizer = tf.train.adam();
//   model.compile({
//     optimizer: optimizer,
//     loss: 'categoricalCrossentropy',
//     metrics: ['accuracy'],
//   });
//
//   return model;
// }

function _lowerCaseToCamelCase(str) {
  return str.replace(/_([a-z])/g, function (g) { return g[1].toUpperCase(); });
}

async function run() {
  // Check that the model is correct by evaluating it on test data.
  const data = await getData();
  let model = await getModel();
  const accuracy = await getValidationAccuracy(model, data);

  const optimization_data = getOptimizationData();
  model = compileModel(model, optimization_data);

  await retrainModel(model, data);
  const new_accuracy = await getValidationAccuracy(model, data);
}

document.addEventListener('DOMContentLoaded', run);
