class Config {
  private static instance: Config
  protocol: string
  domainName: string
  apiUrl: string


  private constructor() {
    this.protocol = 'http'
    this.domainName = 'localhost:8000'
    this.apiUrl = this.protocol + '://' + this.domainName
  }

  public static getInstance(): Config {
    if (!Config.instance) {
      Config.instance = new Config()
    }
    return Config.instance
  }
}

export default Config.getInstance()


