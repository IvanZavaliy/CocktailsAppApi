package ua.ivanzav

import io.ktor.server.application.*
import io.ktor.server.response.*
import io.ktor.server.routing.*

fun Application.configureRouting() {
    MongoDatabase.init(this.environment)

    routing {
        route("/api/json/v1/1") {
            get("/filter.php") {
                val a = call.request.queryParameters["a"]
                val i = call.request.queryParameters["i"]
                
                when {
                    a != null -> {
                        val drinks = MongoDatabase.getDrinksByAlcoholic(a)
                        call.respond(DrinksBriefResponse(drinks))
                    }
                    i != null -> {
                        val drinks = MongoDatabase.getDrinksByIngredient(i)
                        call.respond(DrinksBriefResponse(drinks))
                    }
                    else -> call.respond(DrinksBriefResponse(emptyList()))
                }
            }
            
            get("/lookup.php") {
                val i = call.request.queryParameters["i"]
                if (i != null) {
                    val drinks = MongoDatabase.getDrinkById(i)
                    call.respond(DrinksFullResponse(drinks))
                } else {
                    call.respond(DrinksFullResponse(emptyList()))
                }
            }
            
            get("/search.php") {
                val s = call.request.queryParameters["s"]
                if (s != null) {
                    val drinks = MongoDatabase.searchDrinksByName(s)
                    call.respond(DrinksFullResponse(drinks))
                } else {
                    call.respond(DrinksFullResponse(emptyList()))
                }
            }
            
            get("/list.php") {
                val i = call.request.queryParameters["i"]
                if (i == "list") {
                    val ingredients = MongoDatabase.getIngredientsList()
                    call.respond(IngredientsBriefResponse(ingredients))
                } else {
                    call.respond(IngredientsBriefResponse(emptyList()))
                }
            }
        }
        
        get("/") {
            call.respondText("Cocktails API is running!")
        }
    }
}