from GameOfLife import GameOfLife

#gameoflife = GameOfLife(filepath='heart.txt', resolution=(720, 720), background_color=(255, 255, 255), cell_color=(203, 192, 255))
gameoflife = GameOfLife(filepath='heart.txt', resolution=(720, 720), background_color=(165, 194, 164), cell_color=(203, 192, 255))

gameoflife.run(fps=10)