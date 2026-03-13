#!/bin/bash

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
ENVIRONMENT=${1:-staging}
IMAGE_TAG=${2:-latest}
REGISTRY=${REGISTRY:-ghcr.io}
REPOSITORY=${REPOSITORY:-$GITHUB_REPOSITORY}

# Service names
SERVICES=("api" "bot" "web")

print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_dependencies() {
    local deps=("docker" "docker-compose" "curl")
    for dep in "${deps[@]}"; do
        if ! command -v "$dep" &> /dev/null; then
            print_error "$dep is not installed"
            exit 1
        fi
    done
    print_info "All dependencies are installed"
}

load_environment() {
    local env_file=".env.$ENVIRONMENT"

    if [ ! -f "$env_file" ]; then
        print_warning "Environment file $env_file not found, using .env.example"
        env_file=".env.example"
    fi

    if [ ! -f "$env_file" ]; then
        print_error "No environment file found"
        exit 1
    fi

    # Load environment variables
    export $(grep -v '^#' "$env_file" | xargs)
    print_info "Loaded environment from $env_file"
}

update_docker_compose() {
    local compose_file="docker-compose.$ENVIRONMENT.yml"

    if [ ! -f "$compose_file" ]; then
        print_info "Using default docker-compose.yml"
        compose_file="docker-compose.yml"
    fi

    # Update image tags in docker-compose
    for service in "${SERVICES[@]}"; do
        local image_name="$REGISTRY/$REPOSITORY/$service:$IMAGE_TAG"
        print_info "Setting $service image to $image_name"
        export "${service^^}_IMAGE"="$image_name"
    done

    echo "$compose_file"
}

run_database_migrations() {
    print_info "Running database migrations..."

    # Wait for database to be ready
    local max_attempts=30
    local attempt=1

    while [ $attempt -le $max_attempts ]; do
        if docker-compose exec -T db pg_isready -U historian &> /dev/null; then
            print_info "Database is ready"
            break
        fi

        print_info "Waiting for database... (attempt $attempt/$max_attempts)"
        sleep 2
        attempt=$((attempt + 1))
    done

    if [ $attempt -gt $max_attempts ]; then
        print_error "Database is not ready after $max_attempts attempts"
        exit 1
    fi

    # Run migrations
    docker-compose run --rm api alembic upgrade head
    print_info "Database migrations completed"
}

deploy_services() {
    local compose_file=$1

    print_info "Deploying services for $ENVIRONMENT environment..."

    # Pull latest images
    print_info "Pulling latest images..."
    docker-compose -f "$compose_file" pull

    # Start services
    print_info "Starting services..."
    docker-compose -f "$compose_file" up -d --remove-orphans

    # Wait for services to be healthy
    print_info "Waiting for services to be healthy..."
    sleep 10

    # Check service health
    for service in "${SERVICES[@]}"; do
        if docker-compose -f "$compose_file" ps "$service" | grep -q "Up (healthy)"; then
            print_info "$service is healthy"
        else
            print_warning "$service health check failed, checking logs..."
            docker-compose -f "$compose_file" logs "$service" --tail=20
        fi
    done
}

rollback() {
    local compose_file=$1
    local previous_tag=$2

    print_error "Deployment failed, rolling back to tag: $previous_tag"

    for service in "${SERVICES[@]}"; do
        local image_name="$REGISTRY/$REPOSITORY/$service:$previous_tag"
        export "${service^^}_IMAGE"="$image_name"
    done

    docker-compose -f "$compose_file" up -d --force-recreate
    print_info "Rollback completed"
}

main() {
    print_info "Starting deployment to $ENVIRONMENT environment with tag: $IMAGE_TAG"

    # Check dependencies
    check_dependencies

    # Load environment
    load_environment

    # Get previous image tag for rollback
    local previous_tag
    previous_tag=$(docker images --format "{{.Tag}}" "$REGISTRY/$REPOSITORY/api" | head -1 || echo "none")

    # Update docker-compose
    local compose_file
    compose_file=$(update_docker_compose)

    # Deploy services
    if deploy_services "$compose_file"; then
        # Run database migrations after successful deployment
        run_database_migrations

        print_info "Deployment completed successfully!"
        print_info "Services are running with tag: $IMAGE_TAG"

        # Show service status
        docker-compose -f "$compose_file" ps
    else
        rollback "$compose_file" "$previous_tag"
        exit 1
    fi
}

# Run main function
main "$@"
