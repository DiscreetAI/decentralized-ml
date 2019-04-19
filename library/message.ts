import { LayersModel } from "@tensorflow/tfjs/dist";

export class DMLRequest {
    round:number;
    constructor (public id:string, public repo: string, public action: string, 
        public params:{[param:string]: any},
        public label_index:number) {
        this.round = -1;
    }

    static serialize(request:DMLRequest, message:string) {
        var socketMessage:any = {
            "id": request.id,
            "repo": request.repo,
            "action": request.action,
            "message": message
        }
        if (request.action == "train")
            socketMessage["round"] = request.round;
        return JSON.stringify(socketMessage);
    }

    /* TODO: This feels more complicated than necessary */
    static deserialize(message:string) {
        var request_json = JSON.parse(message);
        var request:DMLRequest =  new DMLRequest(
            request_json["id"],
            request_json["repo"],
            request_json["action"],
            request_json["params"],
            request_json["label_index"]
        )
        if (request.action == "train") 
            request.round = request_json["round"];
        
            return request;
    }

}