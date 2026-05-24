package ua.ivanzav

import com.mongodb.ConnectionString
import com.mongodb.MongoClientSettings
import com.mongodb.client.model.Filters
import com.mongodb.client.model.Sorts
import com.mongodb.kotlin.client.coroutine.MongoClient
import io.ktor.server.application.*
import kotlinx.coroutines.flow.toList
import kotlinx.coroutines.flow.firstOrNull
import org.bson.Document
import org.bson.codecs.configuration.CodecRegistries
import org.bson.codecs.pojo.PojoCodecProvider
import java.util.regex.Pattern

object MongoDatabase {
    private lateinit var client: MongoClient
    private lateinit var database: com.mongodb.kotlin.client.coroutine.MongoDatabase

    fun init(environment: ApplicationEnvironment) {
        val uri = environment.config.property("mongodb.uri").getString()
        val dbName = environment.config.property("mongodb.database").getString()

        val pojoCodecRegistry = CodecRegistries.fromRegistries(
            MongoClientSettings.getDefaultCodecRegistry(),
            CodecRegistries.fromProviders(PojoCodecProvider.builder().automatic(true).build())
        )

        val settings = MongoClientSettings.builder()
            .applyConnectionString(ConnectionString(uri))
            .codecRegistry(pojoCodecRegistry)
            .build()

        client = MongoClient.create(settings)
        database = client.getDatabase(dbName)
    }

    suspend fun getDrinksByAlcoholic(alcoholic: String): List<DrinkBrief> {
        val collection = database.getCollection<DrinkBrief>("drinks_details")
        val searchString = "^" + alcoholic.replace("_", " ") + "$"
        val pattern = Pattern.compile(searchString, Pattern.CASE_INSENSITIVE)
        return collection.find(Filters.regex("strAlcoholic", pattern))
            .sort(Sorts.ascending("strDrink"))
            .limit(100)
            .toList()
    }

    suspend fun getDrinkById(id: String): List<DrinkDetail> {
        val collection = database.getCollection<DrinkDetail>("drinks_details")
        val drink = collection.find(Filters.eq("idDrink", id)).firstOrNull()
        return if (drink != null) listOf(drink) else emptyList()
    }

    suspend fun searchDrinksByName(name: String): List<DrinkDetail> {
        val collection = database.getCollection<DrinkDetail>("drinks_details")
        val pattern = Pattern.compile(name, Pattern.CASE_INSENSITIVE)
        return collection.find(Filters.regex("strDrink", pattern))
            .sort(Sorts.ascending("strDrink"))
            .toList()
    }

    suspend fun searchDrinksByFirstLetter(letter: String): List<DrinkDetail> {
        val collection = database.getCollection<DrinkDetail>("drinks_details")
        val pattern = Pattern.compile("^$letter", Pattern.CASE_INSENSITIVE)
        return collection.find(Filters.regex("strDrink", pattern))
            .sort(Sorts.ascending("strDrink"))
            .toList()
    }

    suspend fun getIngredientsList(): List<IngredientBrief> {
        val collection = database.getCollection<Document>("ingredients")
        val docs = collection.find()
            .sort(Sorts.ascending("strIngredient"))
            .limit(100)
            .toList()
            
        return docs.map { doc ->
            IngredientBrief(strIngredient1 = doc.getString("strIngredient"))
        }
    }

    suspend fun getDrinksByIngredient(ingredientName: String): List<DrinkBrief> {
        val collection = database.getCollection<DrinkBrief>("drinks_details")
        
        val pattern = Pattern.compile(ingredientName, Pattern.CASE_INSENSITIVE)
        
        // We need to check all 15 ingredient fields
        val filters = (1..15).map { i ->
            Filters.regex("strIngredient$i", pattern)
        }
        
        return collection.find(Filters.or(filters))
            .sort(Sorts.ascending("strDrink"))
            .limit(100)
            .toList()
    }
}
