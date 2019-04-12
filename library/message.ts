class DMLMessage {
    constructor (public id:string, public repo: string, public type: string) {

    }
}

class DMLRequest extends DMLMessage {
    constructor (id:string, public repo: string, public type: string, public model:object) {
        super(id, repo, type);
    }
}