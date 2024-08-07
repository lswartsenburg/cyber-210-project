import structlog
log = structlog.get_logger()

if __name__ == "__main__":
  log.info("hello, %s!", "pretty log", key="value!", more_than_strings=[1, 2, 3])  
  log.info("let's")  
  log.info("add")  
  log.info("a")  
  log.info("breakpoint")  