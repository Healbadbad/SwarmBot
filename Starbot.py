import cybw
from CombatManager import CombatManager
import threading
from time import sleep

client = cybw.BWAPIClient
Broodwar = cybw.Broodwar

class Starbot(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        # self.instance = instance


    def reconnect(self):
        while not client.connect():
            sleep(0.5)

    def showPlayers(self):
        players = Broodwar.getPlayers()
        for player in players:
            Broodwar << "Player [" << player.getID() << "]: " << player.getName(
                ) << " is in force: " << player.getForce().getName() << "\n"

    def showForces(self):
        forces = Broodwar.getForces()
        for force in forces:
            players = force.getPlayers()
            Broodwar << "Force " << force.getName() << " has the following players:\n"
            for player in players:
                Broodwar << "  - Player [" << player.getID() << "]: " << player.getName() << "\n"

    def drawStats(self):
        line = 0
        allUnitTypes = cybw.UnitTypes.allUnitTypes()
        Broodwar.drawTextScreen(cybw.Position(5, 0), "I have " +
            str(Broodwar.self().allUnitCount())+" units:")
        for unitType in allUnitTypes:
            count = Broodwar.self().allUnitCount(unitType)
            if count > 0:
                line += 1
                statStr = "- "+str(count)+" "+str(unitType)
                Broodwar.drawTextScreen(cybw.Position(5, 12*line), statStr)

    def drawBullets(self):
        bullets = Broodwar.getBullets()
        for bullet in bullets:
            p = bullet.getPosition()
            velocityX = bullet.getVelocityX()
            velocityY = bullet.getVelocityY()
            lineColor = cybw.Colors.Red
            textColor = cybw.Text.Red
            if bullet.getPlayer == Broodwar.self():
                lineColor = cybw.Colors.Green
                textColor = cybw.Text.Green
            Broodwar.drawLineMap(p, p+cybw.Position(velocityX, velocityY), lineColor)
            Broodwar.drawTextMap(p, chr(textColor) + str(bullet.getType()))

    def drawVisibilityData(self):
        wid = Broodwar.mapWidth()
        hgt = Broodwar.mapHeight()
        for x in range(wid):
            for y in range(hgt):
                drawColor = cybw.Colors.Red
                if Broodwar.isExplored(tileX=x, tileY=y):
                    if Broodwar.isVisible(tileX=x, tileY=y):
                        drawColor = cybw.Colors.Green
                    else:
                        drawColor = cybw.Colors.Blue

                Broodwar.drawDotMap(cybw.Position(x*32+16, y*32+16), drawColor)

    def getScore(self):
        return 5

    def run(self):
        print("Connecting...")
        self.reconnect()
        while True:
            print("waiting to enter match")
            while not Broodwar.isInGame():
                client.update()
                if not client.isConnected():
                    print("Reconnecting...")
                    self.reconnect()
                else:
                    from array import array
                    # print(bytes("MarinesEven.scm",'utf-8'))
                    # Broodwar.setMap(bytes("C:\\Program Files (x86)\\StarCraft\\Maps\\Setups\\MarinesEven.scm",'utf-8'))
            print("starting match!")
            Broodwar.sendText( "Hello world from python!")
            Broodwar.printf( "Hello world from python!")

            # need newline to flush buffer
            Broodwar << "The map is " << Broodwar.mapName() << ", a " \
                << len(Broodwar.getStartLocations()) << " player map" << " \n"

            # Enable some cheat flags
            Broodwar.enableFlag(cybw.Flag.UserInput)


            show_bullets = False
            show_visibility_data = False

            # Set Variables for game speed, and automap switching
            Broodwar.setLocalSpeed(0)


            if Broodwar.isReplay():
                Broodwar << "The following players are in this replay:\n"
                players = Broodwar.getPlayers()
                # TODO add rest of replay actions

            else: # 
                Broodwar << "The matchup is " << Broodwar.self().getRace() << " vs " << Broodwar.enemy().getRace() << "\n"
                # send each worker to the mineral field that is closest to it
                # reload(Comba)
                commander = CombatManager()
                units    = Broodwar.self().getUnits()
                minerals  = Broodwar.getMinerals()
                print("got", len(units), "units")
                print("got", len(minerals), "minerals")
                for unit in units:
                    if unit.getType().isWorker():
                        closestMineral = None
                        # print("worker")
                        for mineral in minerals:
                            if closestMineral is None or unit.getDistance(mineral) < unit.getDistance(closestMineral):
                                closestMineral = mineral
                        if closestMineral:
                            unit.rightClick(closestMineral)
                    elif unit.getType().isResourceDepot():
                        unit.train(Broodwar.self().getRace().getWorker())
                events = Broodwar.getEvents()
                print(len(events))
            # Broodwar.restartGame()

            while Broodwar.isInGame():
                # Broodwar.restartGame()

            # Broodwar.setMap(bytes("MarinesEven.scm",'utf-8'))
                Broodwar.setMap(bytes("C:\\Program Files (x86)\\StarCraft\\Maps\\Setups\\MarinesEven.scm",'utf-8'))

                events = Broodwar.getEvents()
                for e in events:
                    eventtype = e.getType()

                    if eventtype == cybw.EventType.MatchEnd: # TODO: Signal The Combat Manager the score
                        if e.isWinner():
                            Broodwar << "I won the game\n"
                            commander.signalVictory()
                        else:
                            Broodwar << "I lost the game\n"
                            commander.signalDefeat()
                        Broodwar.restartGame()


                    elif eventtype == cybw.EventType.SendText:
                        if e.getText() == "/show bullets":
                            show_bullets = not show_bullets
                        elif e.getText() == "/show players":
                            showPlayers()
                        elif e.getText() == "/show forces":
                            showForces()
                        elif e.getText() == "/show visibility":
                            show_visibility_data = not show_visibility_data
                        elif e.getText() == "/reload":
                            #Todo: Update this for dynamic reloading
                            reload(CombatManager)
                        elif e.getText() == "/attack":
                            Broodwar << "ATTACK!!!"
                            if len(e.getText().split(" ")) > 2:
                                commander.setAttackPos(int(e.getText().split(" ")[1]), int(e.getText().split(" ")[2]))
                        else:
                            pass
                            # Broodwar << "You typed \"" << e.getText() << "\"!\n"

                    elif eventtype == cybw.EventType.ReceiveText:
                        pass
                        # Broodwar << e.getPlayer().getName() << " said \"" << e.getText() << "\"\n"
                        

                    elif eventtype == cybw.EventType.PlayerLeft:
                        Broodwar << e.getPlayer().getName() << " left the game.\n"

                    elif eventtype == cybw.EventType.NukeDetect:
                        if e.getPosition() is not cybw.Positions.Unknown:
                            Broodwar.drawCircleMap(e.getPosition(), 40,
                                cybw.Colors.Red, True)
                            Broodwar << "Nuclear Launch Detected at " << e.getPosition() << "\n"
                        else:
                            Broodwar << "Nuclear Launch Detected.\n"

                    elif eventtype == cybw.EventType.UnitCreate:
                        commander.takeUnit(e.getUnit())
                        if not Broodwar.isReplay():
                            pass
                            # Broodwar << "A " << e.getUnit() << " has been created at " << e.getUnit().getPosition() << "\n"
                        else:
                            if(e.getUnit().getType().isBuilding() and
                              (e.getUnit().getPlayer().isNeutral() == False)):
                                seconds = Broodwar.getFrameCount()/24
                                minutes = seconds/60
                                seconds %= 60
                                Broodwar.sendText(str(minutes)+":"+str(seconds)+": "+e.getUnit().getPlayer().getName()+" creates a "+str(e.getUnit().getType())+"\n")
                    
                    elif eventtype == cybw.EventType.UnitDestroy:
                        commander.removeUnit(e.getUnit())
                        if not Broodwar.isReplay():
                            pass
                            # Broodwar << "A " << e.getUnit() << " has been destroyed at " << e.getUnit().getPosition() << "\n"


                    
                    elif eventtype == cybw.EventType.UnitMorph:
                        if not Broodwar.isReplay():
                            pass
                            # Broodwar << "A " << e.getUnit() << " has been morphed at " << e.getUnit().getPosition() << "\n"
                        else:
                            # if we are in a replay, then we will print out the build order
                            # (just of the buildings, not the units).
                            if e.getUnit().getType().isBuilding() and not e.getUnit().getPlayer().isNeutral():
                                seconds = Broodwar.getFrameCount()/24
                                minutes = seconds/60
                                seconds %= 60
                                Broodwar << str(minutes) << ":" << str(seconds) << ": " << e.getUnit().getPlayer().getName() << " morphs a " << e.getUnit().getType() << "\n"
                    
                    elif eventtype == cybw.EventType.UnitShow:
                        if not Broodwar.isReplay():
                            pass
                            #Broodwar << e.getUnit() << " spotted at " << e.getUnit().getPosition() << "\n"
                    
                    elif eventtype == cybw.EventType.UnitHide:
                        if not Broodwar.isReplay():
                            pass
                            # Broodwar << e.getUnit() << " was last seen at " << e.getUnit().getPosition() << "\n"
                   
                    elif eventtype == cybw.EventType.UnitRenegade:
                        if not Broodwar.isReplay():
                            pass
                            # Broodwar << e.getUnit() << " is now owned by " << e.getUnit().getPlayer() << "\n"
                    
                    elif eventtype == cybw.EventType.SaveGame:
                        Broodwar << "The game was saved to " << e.getText() << "\n"

                if show_bullets:
                    drawBullets()
                if show_visibility_data:
                    drawVisibilityData()
                self.drawStats()
                Broodwar.drawTextScreen(cybw.Position(300, 0), "FPS: " +
                    str(Broodwar.getAverageFPS()))
                # Run the combatManager
                commander.update()

                client.update()
