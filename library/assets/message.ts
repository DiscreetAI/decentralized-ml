import { LayersModel } from "@tensorflow/tfjs/dist";

export class DMLRequest {
    round:number;
    constructor (public id:string, public repo: string, public action: string, 
        public params:{[param:string]: any}) {
        this.round = -1;
    }

    static _serialize(request:DMLRequest, message:any) {
        var socketMessage:any = {
            "session_id": request.id,
            "repo": request.repo,
            "action": request.action,
            "results": message,
            "type": "NEW_WEIGHTS"
        }
        if (request.action == "TRAIN")
            socketMessage["round"] = request.round;
        return JSON.stringify(socketMessage);
    }

    /* TODO: This feels more complicated than necessary */
    static _deserialize(message:string) {
        var request_json = JSON.parse(message);
        var request:DMLRequest =  new DMLRequest(
            request_json["session_id"],
            request_json["repo"],
            request_json["action"],
            request_json["hyperparams"]
        )
        if (request.action == "TRAIN") 
            request.round = request_json["round"];
        
        return request;
    }

}