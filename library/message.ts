import { LayersModel } from "@tensorflow/tfjs/dist";

class DMLMessage {
    constructor (public id:string, public repo: string, public type: string) {

    }
}

export class DMLRequest extends DMLMessage {
    constructor (id:string, repo: string, type: string, public model:LayersModel, 
        public round:number, public params:{[param:string]: any}, public label_index:number) {
        super(id, repo, type);
    }
}

export class DMLResult extends DMLMessage {
    constructor (id:string, repo: string, type: string, public message:object) {
        super(id, repo, type);
    }
}