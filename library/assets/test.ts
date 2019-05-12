import { DMLDB } from "./dml_db.js";
import { loadLayersModel, tensor} from '@tensorflow/tfjs';

async function run () {
    var db:DMLDB = new DMLDB();
    await db.open()

    var data = tensor([[1, 2], [3, 4]]).as2D(2, 2);
    db.create("test", data);
    console.log(data.print());
}


document.addEventListener('DOMContentLoaded', run);


